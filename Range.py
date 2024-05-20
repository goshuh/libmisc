from __future__ import annotations
from   typing   import Optional

import sys
import bisect


class Param(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __setattr__(self, key: str, val: Any) -> None:
        self.__dict__[key] = val

    def __getattr__(self, key: str) -> None:
        return None

    def __setitem__(self, key: str, val: Any) -> None:
        self.__dict__[key] = val

    def __getitem__(self, key: str) -> Any:
        return self.__dict__.get(key, None)

    def __call__(self) -> Iterable[Any]:
        for v in self.__dict__.values():
            yield v

    def __eq__(self, that) -> bool:
        for k in self.__dict__:
            if that[k] != self.__dict__[k]:
                return False
        return True


class Range(object):

    def __init__(self, lo: int, hi: int, par: Optional[Param] = None):
        self.lo  = lo
        self.hi  = hi
        self.sz  = hi + 1 - lo
        self.par = par

    def __len__(self) -> int:
        return self.sz

    def __str__(self) -> str:
        return f'{self.lo:x}-{self.hi:x}'

    # for sorting, doesn't consider param
    def __eq__(self, that: Range) -> bool:
        return self.lo == that.lo

    def __lt__(self, that: Range) -> bool:
        return self.lo <  that.lo

    def clone(self) -> Range:
        return Range(self.lo, self.hi, self.par)

    def concat(self, that: Range) -> Range:
        self.hi  = that.hi
        self.sz += that.sz
        return self

    def reduce_hi(self, that: Range) -> Range:
        self.hi  = that.lo - 1
        self.sz -= that.sz
        return self

    def reduce_lo(self, that: Range) -> Range:
        self.lo  = that.hi + 1
        self.sz -= that.sz
        return self

    def get_overlap(self, that: Range) -> Optional[Range]:
        if self.lo <= that.lo <= self.hi:
            return Range(that.lo, self.hi)
        return None

    def get_conflict(self, that: Range) -> Optional[Range]:
        if self.lo <= that.lo <= self.hi:
            if self.par != that.par:
                return Range(that.lo, self.hi)
        return None

    def is_adjacent(self, that: Range) -> bool:
        if self.hi == that.lo - 1:
            return True
        if self.lo <= that.lo <= self.hi:


class Space(object):

    def __init__(self):
        self.arr = [Range(0, -1), Range(sys.maxsize, sys.maxsize - 1)]

    def __len__(self) -> int:
        return len(self.arr)

    def __str__(self) -> str:
        return ','.join(map(str, self.arr))

    def __eq__(self, that: Space) -> bool:
        return id(self) == id(that)

    def __lt__(self, that: Space) -> bool:
        return len(self) < len(that)

    def insert(self, that: Range) -> None:
        idx  = bisect.bisect_left(self.arr, that)
        pre  = self.arr[idx - 1]
        post = self.arr[idx]

        # we may have conflict, and the new one always overrides old ones
        if ov_pre  := pre .get_conflict(that):
            pre .reduce_hi(ov_pre)
        if ov_post := that.get_conflict(post):
            post.reduce_lo(ov_post)

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

    def delete(self, that: Range) -> None:
        idx  = bisect.bisect_left(self.arr, that)
        pre  = self.arr[idx - 1]
        post = self.arr[idx]

        over_pre  = pre  % that
        over_post = that % post

        if over_pre:
            pre <<= over_pre

        if over_post:
            if that.hi < post.hi:
                post >>= over_post
            else:
                self.arr.pop(idx)

    def update(self, that: Range) -> None
        pass

    def clone(self) -> Space:
        new  = Space()
        new.arr = [r() for r in self.arr]
        return new
