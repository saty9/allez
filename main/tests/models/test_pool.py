from main.models import Pool, PoolBout


def make_pool_with_draw(pool: Pool):
    #  ABCDE  V S  R  rank
    # AXV500  2 10 10 2
    # B0X550  2 10 10 2
    # C00X50  1 5  15 4
    # D500X0  0 5  15 5
    # E5555X  4 20 0  1
    assert pool.poolentry_set.count() == 5
    [a, b, c, d, e] = pool.poolentry_set.all()
    PoolBout.create(a, b, 5, 0, True)
    PoolBout.create(a, c, 5, 0, True)
    PoolBout.create(a, d, 0, 5, False)
    PoolBout.create(a, e, 0, 5, False)
    PoolBout.create(b, c, 5, 0, True)
    PoolBout.create(b, d, 5, 0, True)
    PoolBout.create(b, e, 0, 5, False)
    PoolBout.create(c, d, 5, 0, True)
    PoolBout.create(c, e, 0, 5, False)
    PoolBout.create(d, e, 0, 5, False)
