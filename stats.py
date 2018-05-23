import inspect
from io import TextIOWrapper  # noqa: F401
import itertools
import linecache
from os import path
from typing import Callable, Iterable, TextIO, Union  # noqa: F401
import re
from _wsgi_lineprof import LineProfiler as _LineProfiler
from wsgi_profiler.filters import BaseFilter


class LineProfilerStat(object):
    def __init__(self, filename, name, firstlineno, timings):
        self.filename = filename
        self.name = name
        self.firstlineno = firstlineno
        self.timings = timings
        self.total_time = sum(t.total_time for t in timings.values())
        self.total_time *= _LineProfiler.get_unit()

    def get_mongo_profiling(self, code):
        """
        this method is used to get the profiling for mongo
        the regex link is here -> https://regex101.com/r/ZiG085/3
        """
        regex = r"(.objects(.get)?\(|.aggregate|.find(_one)?\(|.(update)\(\s*{|.(insert)\({)"
        matches = re.finditer(regex, code, re.MULTILINE | re.IGNORECASE | re.VERBOSE)
        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1
            matched_text = match.group()
            if "update" in matched_text :
                if code.count("{") > 1 or "$set" in code:
                    return True, "Update"
                else:
                    return False, ""
            elif "insert" in matched_text :
                return True, "Insert"
            else:
                return True, "Query"
        return False, ""
        
        
    def write_text(self, stream):
        if not path.exists(self.filename):
            stream.write("ERROR: %s\n" % self.filename)
            return
        stream.write("File: %s\n" % self.filename)
        stream.write("Name: %s\n" % self.name)
        stream.write("Total time: %g [sec]\n" % self.total_time)

        linecache.clearcache()
        lines = linecache.getlines(self.filename)
        if self.name != "<module>":
            lines = inspect.getblock(lines[self.firstlineno - 1:])

        template = '%6s %9s %12s %12s  %-s'
        header = template % ("Line", "Hits", "Time", "Mongo", "Code")
        stream.write(header)
        stream.write("\n")
        stream.write("=" * len(header))
        stream.write("\n")

        d = {}
        for i, code in zip(itertools.count(self.firstlineno), lines):
            timing = self.timings.get(i)
            if timing is None:
                d[i] = {
                    "hits": "",
                    "time": "",
                    "code": code,
                    "mongo":""
                }
            else:
                mongo_profiling = ""
                mongo_connection, opration = self.get_mongo_profiling(code)
                if mongo_connection:
                    mongo_profiling = opration
                d[i] = {
                    "hits": timing.n_hits,
                    "time": timing.total_time,
                    "code": code,
                    "mongo":mongo_profiling
                }
        for i in sorted(d.keys()):
            r = d[i]
            stream.write(template % (i, r["hits"], r["time"], r["mongo"],r["code"]))
        stream.write("\n")


CallableFilterType = Callable[[Iterable[LineProfilerStat]],
                              Iterable[LineProfilerStat]]
FilterType = Union[CallableFilterType, BaseFilter]


class LineProfilerStats(object):
    def __init__(self, stats):
        # type: (Iterable[LineProfilerStat]) -> None
        self.stats = stats

    def write_text(self, stream):
        # type: (Union[TextIO, TextIOWrapper]) -> None
        stream.write("Time unit: %s [sec]\n\n" % _LineProfiler.get_unit())
        for stat in self.stats:
            stat.write_text(stream)

    def filter(self, f):
        # type: (FilterType) -> LineProfilerStats
        if isinstance(f, BaseFilter):
            return LineProfilerStats(f.filter(self.stats))
        else:
            return LineProfilerStats(f(self.stats))
