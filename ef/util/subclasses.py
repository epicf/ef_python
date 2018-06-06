def get_all_subclasses(cls):
    subclasses = set()
    todo = [cls]
    while todo:
        parent = todo.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                todo.append(child)
    return subclasses