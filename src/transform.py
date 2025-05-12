"""Module provide functions to conver data to pandas DataFrame and transform them"""

import json
import logging
import os
import sys

import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from config import your_config_module

logger = logging.getLogger(__name__)  # Get logger for this module


def convert_list_to_dataframe(
    data_list: list | None, entity_name: str
) -> pd.DataFrame | None:
    """Converts and logs python data (list of dicts) to Pandas DataFrame
    Args:
        data: Data to conversion (json files)

    Returns:
    pd.DataFrame: DataFrame made from data or None in case of data failure.
    """
    if data_list is None:
        logger.warning("No data (None) for entity conversion '%s'.", entity_name)
        return None
    if not isinstance(data_list, list):
        logger.warning(
            "Entity data '%s' are not a list(type: %s. Cannot convert.",
            entity_name,
            type(data_list),
        )
        return None
    if not data_list:  # Empty list control
        logger.warning("Entity list '%s' is empy.", entity_name)
        return None  # Possible return empty DataFrame or None

    try:
        df = pd.DataFrame(data_list)
        logger.info("Data '%s' succesfully converted to DataFrame.", entity_name)
        return df
    except Exception as e:
        logger.error("Error during conversion '%s' to DataFrame: %s", entity_name, e)
        return None


def transform_users(users_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Transform users DataFrame"""
    if users_df is None:
        return None
    try:
        # logger.info("Users data transofrmation...")
        # Columns to picks
        relevant_cols = [
            "id",  # User ID
            "firstName",  # First Name
            "lastName",  # Last Name
            "email",  # Email
            "phone",  # Phone
            "gender",  # Gender
            "age",  # Age
            "address.city",  # City
            "address.state",  # State
            "address.postalCode",  # Postal Code
            "birthDate",  # Birth Date (Proxy for Signup Date)
        ]
        # Select only colums which exists in df
        cols_to_select = [col for col in relevant_cols if col in users_df.columns]
        users_df = users_df[cols_to_select]
        # Renaming columns to snake_case
        users_df = users_df.rename(
            columns={
                "id": "user_id",
                "firstName": "first_name",
                "lastName": "last_name",
                "address.city": "city",
                "address.state": "state",
                "address.postalCode": "postal_code",
                "address.coordinates": "coordinates",
                "birthDate": "birth_date",
            }
        )
        # Datatype change
        users_df["birth_date"] = pd.to_datetime(users_df["birth_date"])
        # logger.info("Successful user transformation\n")
        return users_df

    except Exception as e:
        logger.error("Error during user data transformation: %s", e)
        return None


def transform_products(products_df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Transform products DataFrame"""
    if products_df is None:
        return None
    try:
        logger.info("Products data transformation...")

        # Picking columns to keep
        cols_to_keep = [
            "id",
            "title",
            "category",
            "price",
            "discountPercentage",
            "rating",
            "stock",
            "brand",
            "reviews",
        ]
        # Check if columns exists
        existing_cols = [col for col in cols_to_keep if col in products_df.columns]
        products_df = products_df[existing_cols].copy()

        # Renaming columns to snake_case
        products_df = products_df.rename(
            columns={"discountPercentage": "discount_percentage"}
        )  # Upraveno na snake_case

        # Chenge data type
        products_df["price"] = pd.to_numeric(products_df["price"], errors="coerce")
        products_df["discount_percentage"] = pd.to_numeric(
            products_df["discount_percentage"], errors="coerce"
        )
        products_df["rating"] = pd.to_numeric(products_df["rating"], errors="coerce")
        products_df["stock"] = pd.to_numeric(
            products_df["stock"], errors="coerce"
        ).astype("Int64")

        # --- Processing reviews ---
        if "reviews" in products_df.columns:
            logger.info("Processing column 'reviews'...")

            # Count number of reviews and add as new column
            count_reviews = lambda review_list: (
                len(review_list) if isinstance(review_list, list) else 0
            )
            products_df["nr_of_reviews"] = products_df["reviews"].apply(count_reviews)
            logger.info("Column 'nr_of_reviews' created with review counts.")

            # Function for extraction comments -> list of str
            get_comments = lambda review_list: (
                [
                    review.get("comment", "")
                    for review in review_list
                    if isinstance(review, dict)
                ]
                if isinstance(review_list, list)
                else []
            )

            # Create a column with comments (on the copy)
            products_df["review_comments"] = products_df["reviews"].apply(get_comments)
            logger.info("Column 'review_comments' created.")

            # Joining comments to one string
            products_df["review_comments"] = products_df["review_comments"].apply(
                lambda comments: " | ".join(comments)
            )
            logger.info("Column 'review_comments' joined to str.")

            # --- Drop reviews column ---
            products_df = products_df.drop(columns=["reviews"])
            logger.info("Column 'reviews' was successfully dropped.")
        else:
            logger.warning("Column 'reviews' was not found.")
            # If no reviews column, create nr_of_reviews with 0
            products_df["nr_of_reviews"] = 0

        # Drop duplicates ID
        products_df = products_df.drop_duplicates(subset=["id"])
        # logger.info("Successful products transformation\n")
        return products_df  # return transtform DataFrame

    except Exception as e:
        logger.error("Error during products data transformation: %s", e)
        return None


def transform_carts(
    carts_df_raw: pd.DataFrame | None,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Transform products DataFrame.
    Return two DataFrames: one for carts (carts) a second for items in carts (cart_items).
    """
    if carts_df_raw is None:
        return None, None
    try:
        logger.info("Carts data transofrmation...")
        # PART 1: info about carts
        logger.info("Cleaning data for 'carts' table...")
        # Columns pick for carts
        cols_for_carts = [
            "id",  # Cart ID
            "userId",  # Users ID
            "total",  # Total Price for the cart
            "discountedTotal",  # Total Price after Discount
            "totalProducts",  # Product Count
            "totalQuantity",  # Quantity Count
        ]

        # Select only colums which exists in df
        cols_to_select = [col for col in cols_for_carts if col in carts_df_raw.columns]
        carts_cleaned = carts_df_raw[cols_to_select].copy()
        carts_cleaned = carts_cleaned.rename(
            columns={
                "id": "cart_id",
                "userId": "user_id",
                "total": "cart_total",
                "discountedTotal": "discounted_total",
                "totalProducts": "total_products",
                "totalQuantity": "total_quantity",
            }
        )
        # data types change for carts_cleaned
        if "user_id" in carts_cleaned.columns:
            carts_cleaned["user_id"] = pd.to_numeric(
                carts_cleaned["user_id"], errors="coerce"
            ).astype("Int64")
        if "total" in carts_cleaned.columns:
            carts_cleaned["total"] = pd.to_numeric(carts_cleaned["total"])
        if "discounted_total" in carts_cleaned.columns:
            carts_cleaned["discounted_total"] = pd.to_numeric(
                carts_cleaned["discounted_total"]
            )
        if "total_products" in carts_cleaned.columns:
            carts_cleaned["total_products"] = pd.to_numeric(
                carts_cleaned["total_products"]
            ).astype("Int64")
        if "total_quantity" in carts_cleaned.columns:
            carts_cleaned["total_quantity"] = pd.to_numeric(
                carts_cleaned["total_quantity"]
            ).astype("Int64")

        # PART 2: Making carts_items_cleanes
        logger.info("Data normalization for 'cart_items'...")
        cart_items_list = []
        for _, cart_row in carts_df_raw.iterrows():  # iteration over original df
            cart_id = cart_row["id"]
            # Check if collumn exists and its a list
            if "products" in cart_row and isinstance(cart_row["products"], list):
                for product in cart_row[
                    "products"
                ]:  # iteration over list of products in selected cart
                    cart_items_list.append(
                        {
                            "cart_id": cart_id,
                            "product_id": product.get("id"),
                            "title": product.get("title"),
                            "quantity": product.get("quantity"),
                            "price": product.get("price"),  # price of product
                            "total": product.get(
                                "total"
                            ),  # total price for product (quantity * price)
                            "discount_percentage": product.get("discountPercentage"),
                            "discounted_price": product.get(
                                "discountedTotal"
                            ),  # discoundet product price
                        }
                    )
            else:
                logger.warning("Cart Id %d is not a valid list of product.", cart_id)

        # Create DataFrame for cart items
        if not cart_items_list:
            logger.warning(
                "Items in carts was not found, 'cart_items' could not be created."
            )
            cart_items_cleaned = pd.DataFrame(
                columns=[
                    "cart_id",
                    "product_id",
                    "title",
                    "quantity",
                    "price",
                    "total",
                    "discount_percentage",
                    "discounted_price",
                ]
            )  # Empty DF, if items was not found
        else:
            cart_items_cleaned = pd.DataFrame(cart_items_list)
            # Columns rename and datatype change for cart_items
            cart_items_cleaned = cart_items_cleaned.rename(
                columns={
                    "discount_percentage": "discount_percentage",
                    "discounted_price": "discounted_price",
                }
            )
            # Datatype change
            cart_items_cleaned["product_id"] = pd.to_numeric(
                cart_items_cleaned["product_id"]
            ).astype("Int64")
            cart_items_cleaned["quantity"] = pd.to_numeric(
                cart_items_cleaned["quantity"]
            ).astype("Int64")
            cart_items_cleaned["price"] = pd.to_numeric(cart_items_cleaned["price"])
            cart_items_cleaned["total"] = pd.to_numeric(cart_items_cleaned["total"])
            cart_items_cleaned["discount_percentage"] = pd.to_numeric(
                cart_items_cleaned["discount_percentage"]
            )
            cart_items_cleaned["discounted_price"] = pd.to_numeric(
                cart_items_cleaned["discounted_price"]
            )

        return carts_cleaned, cart_items_cleaned

    except Exception as e:
        logger.error("Error during carts data transformation: %s", e)
        # None for both dataframe in case of error
        return None, None


if __name__ == "__main__":
    # basic logging for separate module testing
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    )

    # path to data (relative to transform.py)
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    paths = {
        "users": os.path.join(data_dir, "users_data.json"),
        "products": os.path.join(data_dir, "products_data.json"),
        "carts": os.path.join(data_dir, "carts_data.json"),
    }

    raw_data = {}

    for name, path in paths.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                # read full json a pick key later
                full_data = json.load(f)
                # dummy json returns data with key identical of the endpoint
                raw_data[name] = full_data.get(
                    name, []
                )  # Getting list under the key, default-> empty list
                if not raw_data[name]:
                    logger.warning(
                        "I file %s cant be find data under key '%s'., path, name"
                    )
        except FileNotFoundError as e:
            logger.error("File not found: %s", path)
            raw_data[name] = None
        except json.JSONDecodeError as e:
            logger.error("Error during decoding json file %s: %s", path, e)
            raw_data[name] = None
        except Exception as e:
            logger.error("Unexpected file reading error %s: %s", path, e)
            raw_data[name] = None

    # Convert to DataFrame
    users_df_raw = convert_list_to_dataframe(raw_data.get("users"), "users")
    products_df_raw = convert_list_to_dataframe(raw_data.get("products"), "products")
    carts_df_raw = convert_list_to_dataframe(raw_data.get("carts"), "carts")

    # Transformation
    users_df_cleaned = transform_users(users_df_raw)
    products_df_cleaned = transform_products(products_df_raw)
    carts_df_cleaned, cart_items_df_cleaned = transform_carts(carts_df_raw)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    if users_df_cleaned is not None:
        print("\n--- Cleaned Users ---")
        print(users_df_cleaned.head())
        print(users_df_cleaned.info())

    if products_df_cleaned is not None:
        print("\n--- Cleaned Products ---")
        print(products_df_cleaned.head())
        print(products_df_cleaned.info())
        print(products_df_cleaned[["rating", "review_comments"]].head())

    if carts_df_cleaned is not None:
        print("\n--- Cleaned Carts ---")
        print(carts_df_cleaned.head())
        print(carts_df_cleaned.info())

        # if cart_items_df_cleaned is not None:
        print("\n--- Cleaned Cart Items ---")
        print(cart_items_df_cleaned.head())
        print(cart_items_df_cleaned.info())
