from __future__ import annotations
from   typing   import Optional

import sys
import bisect


class Range(object):

    def __init__(self, lo: int, hi: int):
        assert lo <= hi
        self.lo  = lo
        self.hi  = hi
        self.sz  = hi + 1 - lo

    def __iadd__(self, that: Range) -> Range:
        assert self.hi == that.lo - 1
        self.hi  = that.hi
        self.sz += that.sz
        return self

    def __call__(self) -> Range:
        return Range(self.lo, self.hi)

    def __ilshift__(self, that: Range) -> Range:
        assert self.hi == that.hi and self.lo < that.lo
        self.hi  = that.lo - 1
        self.sz -= that.sz
        return self

    def __irshift__(self, that: Range) -> Range:
        assert self.lo == that.lo and self.hi > that.hi
        self.lo  = that.hi + 1
        self.sz -= that.sz
        return self

    def __len__(self) -> int:
        return self.sz

    def __mod__(self, that: Range) -> Optional[Range]:
        if self.lo <= that.lo <= self.hi:
            return Range(that.lo, self.hi)
        return None

    def __and__(self, that: Range) -> bool:
        return self.hi == that.lo - 1

    def __str__(self) -> str:
        return f'{self.lo:x}-{self.hi:x}'

    def __eq__(self, that: Range) -> bool:
        return self.lo == that.lo

    def __lt__(self, that: Range) -> bool:
        return self.lo <  that.lo


class Space(object):

    def __init__(self):
        self.arr = [Range(0, 0), Range(sys.maxsize, sys.maxsize)]

    def __iadd__(self, that: Range) -> Space:
        idx  = bisect.bisect_left(self.arr, that)
        assert idx >= 1
        pre  = self.arr[idx - 1]
        post = self.arr[idx]
        assert pre  % that is None
        assert that % post is None

        merge_pre  = pre  & that
        merge_post = that & post

        if merge_pre and merge_post:
            pre  += that
            pre  += post
            self.arr[idx - 1] = pre
            self.arr.pop(idx)
        elif merge_pre:
            pre  += that
        elif merge_post:
            that += post
            self.arr[idx] = that
        else:
            self.arr.insert(idx, that)

        return self

    def __isub__(self, that: Range) -> Space:
        idx  = bisect.bisect_left(self.arr, that)
        assert idx >  1
        pre  = self.arr[idx - 1]
        post = self.arr[idx]
        assert that.hi <= post.hi

        over_pre  = pre  % that
        over_post = that % post

        if over_pre:
            pre <<= over_pre
        if over_post:
            if that.hi < post.hi:
                post >>= over_post
            else:
                self.arr.pop(idx)

        return self

    def __call__(self) -> Space:
        new  = Space()
        new.arr = [r() for r in self.arr]
        return new

    def __len__(self) -> int:
        return len(self.arr)

    def __str__(self) -> str:
        return ','.join(map(str, self.arr))

    def __eq__(self, that: Space) -> bool:
        return id(self) == id(that)

    def __lt__(self, that: Space) -> bool:
        return len(self) < len(that)
