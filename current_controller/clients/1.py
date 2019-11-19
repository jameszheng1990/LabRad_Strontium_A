from twisted.internet import reactor,defer, threads
from twisted.internet.task import LoopingCall
import time

def main_loop():
    print('doing stuff in main loop.. do not block me!')

def aBlockingRedisCall(x):
    if x<5: #all connections are busy, try later
        print('%s is less than 5, get a redis client later' % x)
        x+=1
        d = defer.Deferred()
        d.addCallback(aBlockingRedisCall)
        reactor.callLater(1.0,d.callback,x)
        return d

    else: 
        print('got a redis client; doing lookup.. this may take a while')
        def getstuff( x ):
            time.sleep(3)
            return "stuff is %s" % x

        # getstuff is blocking, so you need to push it to a new thread
        d = threads.deferToThread(getstuff, x)
        d.addCallback(gotFinalResult)
        return d

def gotFinalResult(x):
    return 'final result is %s' % x

def result(res):
    print(res)

def aBlockingMethod():
    print('going to sleep...')
    time.sleep(10)
    print('woke up')

def main():
    lc = LoopingCall(main_loop)
    lc.start(2)


    d = defer.Deferred()
    d.addCallback(aBlockingRedisCall)
    d.addCallback(result)
    reactor.callInThread(d.callback, 1)
    reactor.run()

if __name__=='__main__':
    main()