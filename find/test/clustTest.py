import facs
import numpy as np
import random
from scipy.cluster.vq import kmeans2
import sys

# http://blogs.sun.com/yongsun/entry/k_means_and_k_means
def kinit (X, k):
    # init k seeds according to kmeans++
    n = X.shape[0]
    row_max = X.max(axis=1).reshape((-1, 1))
    print 'len(row_max):',len(row_max)

    #choose the 1st seed randomly, and store D(x)^2 in D[]
    centers = [X[random.randint(0,n)]]
    D = [np.absolute((X[i]-centers[0])/row_max[i])**2 for i in range(n)]

    for _ in range(k-1):
        bestDsum = bestIdx = -1

        for i in range(n):
            # Dsum = sum_{x in X} min(D(x)^2,||x-xi||^2)'
            Dsum = reduce(lambda x,y:x+y,
                          (min(D[j], np.absolute((X[j]-X[i])/row_max[i])**2) for j in xrange(n)))

            if bestDsum < 0 or Dsum < bestDsum:
                bestDsum, bestIdx  = Dsum, i

        centers.append (X[bestIdx])
        D = [min(D[i], np.absolute((X[i]-X[bestIdx])/row_max[i])**2) for i in xrange(n)]

    return array (centers)


def main(filename):
    labels, data = facs.loadFacsCSV(filename)
    #res,idx = kmeans2(data, kinit(data,3), minit='points') 
    res,idx = kmeans2(data, 3)
    print 'len(res): ',[len(res[i]) for i in range(len(res))]
    print 'idx:', len(idx)

if __name__ == "__main__": 
    main(sys.argv[1])