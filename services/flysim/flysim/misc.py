from functools import partial
from bson import ObjectId


def set_vars_(drones_collection, _id, what):
    drones_collection.update_one(
        {"_id": _id},
        {"$set": what},
    )


def get_var_(drones_collection, _id, what):
    drone = drones_collection.find_one({"_id": ObjectId(_id)})
    return drone[what]


def set_vars(*args, **kwargs):
    raise RuntimeError("Function not initialized. Call initialize() first")


def get_var(*args, **kwargs):
    raise RuntimeError("Function not initialized. Call initialize() first")


def initialize(drones_collection):
    global set_vars, get_var
    set_vars = partial(set_vars_, drones_collection)
    get_var = partial(get_var_, drones_collection)
