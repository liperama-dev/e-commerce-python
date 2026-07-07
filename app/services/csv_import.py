import csv
import io
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.models import Category, Product
from app.services.security import is_security_threat


def process_csv(decoded_content: str, db: Session) -> dict:
    """
    Parse *decoded_content* as CSV and upsert products into the database.

    Returns a summary dict with imported/discarded counts and discard reasons.
    Uses savepoints per row to allow partial success, and caches categories
    to optimize lookups and avoid session identity map warnings.
    """
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    imported_count = 0
    discarded_count = 0
    discard_reasons: list[dict] = []

    # Cache categories to prevent duplicate lookups and session identity warnings
    categories_cache = {c.name: c for c in db.query(Category).all()}

    for row_num, row in enumerate(csv_reader, start=2):
        # Skip completely blank rows
        if all(v is None or str(v).strip() == "" for v in row.values()):
            continue

        clean_row = {
            k.strip() if k else k: v.strip() if isinstance(v, str) else v
            for k, v in row.items()
            if k
        }
        if not any(clean_row.values()):
            continue

        category_name = clean_row.get("category", "Misc")
        # Ensure category exists in the cache/DB before starting the product savepoint.
        # This keeps the category creation out of the product savepoint so it persists.
        if category_name not in categories_cache:
            try:
                category = Category(name=category_name)
                db.add(category)
                db.flush()
                categories_cache[category_name] = category
            except Exception as e:
                discarded_count += 1
                discard_reasons.append(
                    {"row": row_num, "reason": f"Category creation failed: {e}"}
                )
                continue
        else:
            category = categories_cache[category_name]

        try:
            with db.begin_nested():
                name = clean_row.get("name", "")
                if not name.strip():
                    raise ValueError("Name cannot be empty or whitespace")

                # Security scan on every field
                for k, v in clean_row.items():
                    if isinstance(v, str) and is_security_threat(v):
                        raise ValueError(f"Security threat detected in column '{k}'")

                is_draft = False

                # --- price ---
                try:
                    price_raw = clean_row.get("price", "") or ""
                    price = Decimal(str(price_raw).replace("$", "").replace(",", "") or 0)
                    if price < 0:
                        price = None
                        is_draft = True
                except (ValueError, AttributeError, InvalidOperation):
                    price = None
                    is_draft = True

                # --- stock ---
                try:
                    stock = int(clean_row.get("stock", 0))
                    if stock < 0:
                        stock = None
                        is_draft = True
                except (ValueError, TypeError):
                    stock = None
                    is_draft = True

                # --- weight_kg ---
                try:
                    weight_raw = (clean_row.get("weight_kg") or "").strip()
                    if weight_raw == "":
                        weight_kg = None
                        is_draft = True
                    else:
                        weight_kg = float(weight_raw)
                        if weight_kg < 0:
                            weight_kg = None
                            is_draft = True
                except (ValueError, AttributeError):
                    weight_kg = None
                    is_draft = True

                sku = clean_row.get("sku", "")
                db_product = db.query(Product).filter(Product.sku == sku).first()

                if db_product:
                    db_product.name = clean_row["name"]
                    db_product.description = clean_row.get("description", "")
                    db_product.category_id = category.id
                    db_product.price = price
                    db_product.stock = stock
                    db_product.weight_kg = weight_kg
                    db_product.is_draft = is_draft
                else:
                    new_product = Product(
                        name=clean_row["name"],
                        sku=sku,
                        description=clean_row.get("description", ""),
                        category_id=category.id,
                        price=price,
                        stock=stock,
                        weight_kg=weight_kg,
                        is_draft=is_draft,
                    )
                    db.add(new_product)

                db.flush()  # Push changes to the DB to catch IntegrityErrors, etc.
            imported_count += 1

        except Exception as exc:
            discarded_count += 1
            discard_reasons.append({"row": row_num, "reason": str(exc)})

    # Final commit for all successful rows
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        return {
            "message": "CSV processing failed during final commit",
            "imported_count": 0,
            "discarded_count": discarded_count + imported_count,
            "discard_reasons": [{"row": "all", "reason": str(exc)}],
        }

    return {
        "message": "CSV processed",
        "imported_count": imported_count,
        "discarded_count": discarded_count,
        "discard_reasons": discard_reasons,
    }
