def result(a, b):
    dif = (b-a)%5
    
    if dif == 0:
        return "tie", None
    elif dif <= 2:
        return "loss", dif-1
    elif dif >=3:
        return "win", 1-(dif-3)