from langchain_core.documents import Document

from .. import db


def build_description(car):
    market_category_clause = (
        f", in the {car['market_category']} category"
        if car["market_category"] != "Not Specified"
        else ""
    )

    return (
        f"The {car['year']} {car['make']} {car['model']} is a "
        f"{car['vehicle_size']} {car['vehicle_style']} with a "
        f"{car['engine_hp']:.0f}-HP {car['engine_cylinders']}-cylinder "
        f"{car['engine_fuel_type']} engine, {car['transmission_type']} "
        f"transmission, and {car['driven_wheels']} drivetrain. "
        f"It has {car['number_of_doors']} doors{market_category_clause}. "
        f"EPA-rated at {car['city_mpg']} city / {car['highway_mpg']} highway MPG. "
        f"MSRP: ${car['msrp']:,}."
    )


def build_document(car):
    return Document(page_content=build_description(car), metadata=car)


def build_all_documents():
    return [build_document(car) for car in db.get_all_cars()]


if __name__ == "__main__":
    for document in build_all_documents()[:10]:
        print(document.page_content)
        print()
