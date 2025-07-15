"""
模型共享区
"""
def share_model(name: str, model, source="torch"):
    global shared_models
    if 'shared_models' not in globals():
        shared_models = [{
            "name": name,
            "model": model,
            "source": source}]
        return True
    shared_models.append({
        "name": name,
        "model": model,
        "source": source
        })
def model_exists(name: str):
    global shared_models
    if 'shared_models' not in globals():
        return False
    for shared_model in shared_models:
        if shared_model["name"] == name:
            return True
    return False
def get_model(name: str, view_as=None):
    global shared_models
    if 'shared_models' not in globals():
        return None
    for shared_model in shared_models:
        if shared_model["name"] == name:
            if view_as=="structure":
                return str(shared_model["model"])
            return shared_model["model"]
