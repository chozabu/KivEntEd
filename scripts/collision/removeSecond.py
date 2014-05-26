__author__ = 'chozabu'


def collision_func(space, arbiter):
    scripty.gameref.delObjNext(arbiter.shapes[1].body.data)
