from threading import Thread



def testerfunc():
    print('hihi')
    return testerfunc()

def testfunc():
    print('fack you')
    return "hallo"


t1 = Thread(target=testfunc)
t2 = Thread(target=testerfunc)

t1.run()
