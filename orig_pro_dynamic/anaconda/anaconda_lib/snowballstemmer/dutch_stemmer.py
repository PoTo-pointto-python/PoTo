# self file was generated automatically by the Snowball to Python interpreter

from .basestemmer import BaseStemmer
from .among import Among


class DutchStemmer(BaseStemmer):
    '''
    self class was automatically generated by a Snowball to Python interpreter
    It implements the stemming algorithm defined by a snowball script.
    '''
    serialVersionUID = 1

    a_0 = [
        Among(u"", -1, 6),
        Among(u"\u00E1", 0, 1),
        Among(u"\u00E4", 0, 1),
        Among(u"\u00E9", 0, 2),
        Among(u"\u00EB", 0, 2),
        Among(u"\u00ED", 0, 3),
        Among(u"\u00EF", 0, 3),
        Among(u"\u00F3", 0, 4),
        Among(u"\u00F6", 0, 4),
        Among(u"\u00FA", 0, 5),
        Among(u"\u00FC", 0, 5)
    ]

    a_1 = [
        Among(u"", -1, 3),
        Among(u"I", 0, 2),
        Among(u"Y", 0, 1)
    ]

    a_2 = [
        Among(u"dd", -1, -1),
        Among(u"kk", -1, -1),
        Among(u"tt", -1, -1)
    ]

    a_3 = [
        Among(u"ene", -1, 2),
        Among(u"se", -1, 3),
        Among(u"en", -1, 2),
        Among(u"heden", 2, 1),
        Among(u"s", -1, 3)
    ]

    a_4 = [
        Among(u"end", -1, 1),
        Among(u"ig", -1, 2),
        Among(u"ing", -1, 1),
        Among(u"lijk", -1, 3),
        Among(u"baar", -1, 4),
        Among(u"bar", -1, 5)
    ]

    a_5 = [
        Among(u"aa", -1, -1),
        Among(u"ee", -1, -1),
        Among(u"oo", -1, -1),
        Among(u"uu", -1, -1)
    ]

    g_v = [17, 65, 16, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128]

    g_v_I = [1, 0, 0, 17, 65, 16, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128]

    g_v_j = [17, 67, 16, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128]

    I_p2 = 0
    I_p1 = 0
    B_e_found = False

    def copy_from(self, other):
        self.I_p2 = other.I_p2
        self.I_p1 = other.I_p1
        self.B_e_found = other.B_e_found
        super.copy_from(other)
    

    def r_prelude(self):
        # (, line 41
        # test, line 42
        v_1 = self.cursor
        # repeat, line 42
        try:
            while True:
                try:
                    v_2 = self.cursor
                    try:
                        # (, line 42
                        # [, line 43
                        self.bra = self.cursor
                        # substring, line 43
                        among_var = self.find_among(DutchStemmer.a_0, 11)
                        if among_var == 0:
                            raise lab2()
                        # ], line 43
                        self.ket = self.cursor
                        if among_var == 0:
                            raise lab2()
                        elif among_var == 1:
                            # (, line 45
                            # <-, line 45
                            if not self.slice_from(u"a"):
                                return False
                        elif among_var == 2:
                            # (, line 47
                            # <-, line 47
                            if not self.slice_from(u"e"):
                                return False
                        elif among_var == 3:
                            # (, line 49
                            # <-, line 49
                            if not self.slice_from(u"i"):
                                return False
                        elif among_var == 4:
                            # (, line 51
                            # <-, line 51
                            if not self.slice_from(u"o"):
                                return False
                        elif among_var == 5:
                            # (, line 53
                            # <-, line 53
                            if not self.slice_from(u"u"):
                                return False
                        elif among_var == 6:
                            # (, line 54
                            # next, line 54
                            if self.cursor >= self.limit:
                                raise lab2()
                            self.cursor += 1
                        raise lab1()
                    except lab2: pass
                    self.cursor = v_2
                    raise lab0()
                except lab1: pass
        except lab0: pass
        self.cursor = v_1
        # try, line 57
        v_3 = self.cursor
        try:
            # (, line 57
            # [, line 57
            self.bra = self.cursor
            # literal, line 57
            if not self.eq_s(1, u"y"):
                self.cursor = v_3
                raise lab3()
            # ], line 57
            self.ket = self.cursor
            # <-, line 57
            if not self.slice_from(u"Y"):
                return False
        except lab3: pass
        # repeat, line 58
        try:
            while True:
                try:
                    v_4 = self.cursor
                    try:
                        # goto, line 58
                        try:
                            while True:
                                v_5 = self.cursor
                                try:
                                    # (, line 58
                                    if not self.in_grouping(DutchStemmer.g_v, 97, 232):
                                        raise lab8()
                                    # [, line 59
                                    self.bra = self.cursor
                                    # or, line 59
                                    try:
                                        v_6 = self.cursor
                                        try:
                                            # (, line 59
                                            # literal, line 59
                                            if not self.eq_s(1, u"i"):
                                                raise lab10()
                                            # ], line 59
                                            self.ket = self.cursor
                                            if not self.in_grouping(DutchStemmer.g_v, 97, 232):
                                                raise lab10()
                                            # <-, line 59
                                            if not self.slice_from(u"I"):
                                                return False
                                            raise lab9()
                                        except lab10: pass
                                        self.cursor = v_6
                                        # (, line 60
                                        # literal, line 60
                                        if not self.eq_s(1, u"y"):
                                            raise lab8()
                                        # ], line 60
                                        self.ket = self.cursor
                                        # <-, line 60
                                        if not self.slice_from(u"Y"):
                                            return False
                                    except lab9: pass
                                    self.cursor = v_5
                                    raise lab7()
                                except lab8: pass
                                self.cursor = v_5
                                if self.cursor >= self.limit:
                                    raise lab6()
                                self.cursor += 1
                        except lab7: pass
                        raise lab5()
                    except lab6: pass
                    self.cursor = v_4
                    raise lab4()
                except lab5: pass
        except lab4: pass
        return True

    def r_mark_regions(self):
        # (, line 64
        self.I_p1 = self.limit;
        self.I_p2 = self.limit;
        # gopast, line 69
        try:
            while True:
                try:
                    if not self.in_grouping(DutchStemmer.g_v, 97, 232):
                        raise lab1()
                    raise lab0()
                except lab1: pass
                if self.cursor >= self.limit:
                    return False
                self.cursor += 1
        except lab0: pass
        # gopast, line 69
        try:
            while True:
                try:
                    if not self.out_grouping(DutchStemmer.g_v, 97, 232):
                        raise lab3()
                    raise lab2()
                except lab3: pass
                if self.cursor >= self.limit:
                    return False
                self.cursor += 1
        except lab2: pass
        # setmark p1, line 69
        self.I_p1 = self.cursor
        # try, line 70
        try:
            # (, line 70
            if not self.I_p1 < 3:
                raise lab4()
            self.I_p1 = 3;
        except lab4: pass
        # gopast, line 71
        try:
            while True:
                try:
                    if not self.in_grouping(DutchStemmer.g_v, 97, 232):
                        raise lab6()
                    raise lab5()
                except lab6: pass
                if self.cursor >= self.limit:
                    return False
                self.cursor += 1
        except lab5: pass
        # gopast, line 71
        try:
            while True:
                try:
                    if not self.out_grouping(DutchStemmer.g_v, 97, 232):
                        raise lab8()
                    raise lab7()
                except lab8: pass
                if self.cursor >= self.limit:
                    return False
                self.cursor += 1
        except lab7: pass
        # setmark p2, line 71
        self.I_p2 = self.cursor
        return True

    def r_postlude(self):
        # repeat, line 75
        try:
            while True:
                try:
                    v_1 = self.cursor
                    try:
                        # (, line 75
                        # [, line 77
                        self.bra = self.cursor
                        # substring, line 77
                        among_var = self.find_among(DutchStemmer.a_1, 3)
                        if among_var == 0:
                            raise lab2()
                        # ], line 77
                        self.ket = self.cursor
                        if among_var == 0:
                            raise lab2()
                        elif among_var == 1:
                            # (, line 78
                            # <-, line 78
                            if not self.slice_from(u"y"):
                                return False
                        elif among_var == 2:
                            # (, line 79
                            # <-, line 79
                            if not self.slice_from(u"i"):
                                return False
                        elif among_var == 3:
                            # (, line 80
                            # next, line 80
                            if self.cursor >= self.limit:
                                raise lab2()
                            self.cursor += 1
                        raise lab1()
                    except lab2: pass
                    self.cursor = v_1
                    raise lab0()
                except lab1: pass
        except lab0: pass
        return True

    def r_R1(self):
        if not self.I_p1 <= self.cursor:
            return False
        return True

    def r_R2(self):
        if not self.I_p2 <= self.cursor:
            return False
        return True

    def r_undouble(self):
        # (, line 90
        # test, line 91
        v_1 = self.limit - self.cursor
        # among, line 91
        if self.find_among_b(DutchStemmer.a_2, 3) == 0:
            return False
        self.cursor = self.limit - v_1
        # [, line 91
        self.ket = self.cursor
        # next, line 91
        if self.cursor <= self.limit_backward:
            return False
        self.cursor -= 1
        # ], line 91
        self.bra = self.cursor
        # delete, line 91
        if not self.slice_del():
            return False

        return True

    def r_e_ending(self):
        # (, line 94
        # unset e_found, line 95
        self.B_e_found = False
        # [, line 96
        self.ket = self.cursor
        # literal, line 96
        if not self.eq_s_b(1, u"e"):
            return False
        # ], line 96
        self.bra = self.cursor
        # call R1, line 96
        if not self.r_R1():
            return False
        # test, line 96
        v_1 = self.limit - self.cursor
        if not self.out_grouping_b(DutchStemmer.g_v, 97, 232):
            return False
        self.cursor = self.limit - v_1
        # delete, line 96
        if not self.slice_del():
            return False

        # set e_found, line 97
        self.B_e_found = True
        # call undouble, line 98
        if not self.r_undouble():
            return False
        return True

    def r_en_ending(self):
        # (, line 101
        # call R1, line 102
        if not self.r_R1():
            return False
        # and, line 102
        v_1 = self.limit - self.cursor
        if not self.out_grouping_b(DutchStemmer.g_v, 97, 232):
            return False
        self.cursor = self.limit - v_1
        # not, line 102
        v_2 = self.limit - self.cursor
        try:
            # literal, line 102
            if not self.eq_s_b(3, u"gem"):
                raise lab0()
            return False
        except lab0: pass
        self.cursor = self.limit - v_2
        # delete, line 102
        if not self.slice_del():
            return False

        # call undouble, line 103
        if not self.r_undouble():
            return False
        return True

    def r_standard_suffix(self):
        # (, line 106
        # do, line 107
        v_1 = self.limit - self.cursor
        try:
            # (, line 107
            # [, line 108
            self.ket = self.cursor
            # substring, line 108
            among_var = self.find_among_b(DutchStemmer.a_3, 5)
            if among_var == 0:
                raise lab0()
            # ], line 108
            self.bra = self.cursor
            if among_var == 0:
                raise lab0()
            elif among_var == 1:
                # (, line 110
                # call R1, line 110
                if not self.r_R1():
                    raise lab0()
                # <-, line 110
                if not self.slice_from(u"heid"):
                    return False
            elif among_var == 2:
                # (, line 113
                # call en_ending, line 113
                if not self.r_en_ending():
                    raise lab0()
            elif among_var == 3:
                # (, line 116
                # call R1, line 116
                if not self.r_R1():
                    raise lab0()
                if not self.out_grouping_b(DutchStemmer.g_v_j, 97, 232):
                    raise lab0()
                # delete, line 116
                if not self.slice_del():
                    return False

        except lab0: pass
        self.cursor = self.limit - v_1
        # do, line 120
        v_2 = self.limit - self.cursor
        try:
            # call e_ending, line 120
            if not self.r_e_ending():
                raise lab1()
        except lab1: pass
        self.cursor = self.limit - v_2
        # do, line 122
        v_3 = self.limit - self.cursor
        try:
            # (, line 122
            # [, line 122
            self.ket = self.cursor
            # literal, line 122
            if not self.eq_s_b(4, u"heid"):
                raise lab2()
            # ], line 122
            self.bra = self.cursor
            # call R2, line 122
            if not self.r_R2():
                raise lab2()
            # not, line 122
            v_4 = self.limit - self.cursor
            try:
                # literal, line 122
                if not self.eq_s_b(1, u"c"):
                    raise lab3()
                raise lab2()
            except lab3: pass
            self.cursor = self.limit - v_4
            # delete, line 122
            if not self.slice_del():
                return False

            # [, line 123
            self.ket = self.cursor
            # literal, line 123
            if not self.eq_s_b(2, u"en"):
                raise lab2()
            # ], line 123
            self.bra = self.cursor
            # call en_ending, line 123
            if not self.r_en_ending():
                raise lab2()
        except lab2: pass
        self.cursor = self.limit - v_3
        # do, line 126
        v_5 = self.limit - self.cursor
        try:
            # (, line 126
            # [, line 127
            self.ket = self.cursor
            # substring, line 127
            among_var = self.find_among_b(DutchStemmer.a_4, 6)
            if among_var == 0:
                raise lab4()
            # ], line 127
            self.bra = self.cursor
            if among_var == 0:
                raise lab4()
            elif among_var == 1:
                # (, line 129
                # call R2, line 129
                if not self.r_R2():
                    raise lab4()
                # delete, line 129
                if not self.slice_del():
                    return False

                # or, line 130
                try:
                    v_6 = self.limit - self.cursor
                    try:
                        # (, line 130
                        # [, line 130
                        self.ket = self.cursor
                        # literal, line 130
                        if not self.eq_s_b(2, u"ig"):
                            raise lab6()
                        # ], line 130
                        self.bra = self.cursor
                        # call R2, line 130
                        if not self.r_R2():
                            raise lab6()
                        # not, line 130
                        v_7 = self.limit - self.cursor
                        try:
                            # literal, line 130
                            if not self.eq_s_b(1, u"e"):
                                raise lab7()
                            raise lab6()
                        except lab7: pass
                        self.cursor = self.limit - v_7
                        # delete, line 130
                        if not self.slice_del():
                            return False

                        raise lab5()
                    except lab6: pass
                    self.cursor = self.limit - v_6
                    # call undouble, line 130
                    if not self.r_undouble():
                        raise lab4()
                except lab5: pass
            elif among_var == 2:
                # (, line 133
                # call R2, line 133
                if not self.r_R2():
                    raise lab4()
                # not, line 133
                v_8 = self.limit - self.cursor
                try:
                    # literal, line 133
                    if not self.eq_s_b(1, u"e"):
                        raise lab8()
                    raise lab4()
                except lab8: pass
                self.cursor = self.limit - v_8
                # delete, line 133
                if not self.slice_del():
                    return False

            elif among_var == 3:
                # (, line 136
                # call R2, line 136
                if not self.r_R2():
                    raise lab4()
                # delete, line 136
                if not self.slice_del():
                    return False

                # call e_ending, line 136
                if not self.r_e_ending():
                    raise lab4()
            elif among_var == 4:
                # (, line 139
                # call R2, line 139
                if not self.r_R2():
                    raise lab4()
                # delete, line 139
                if not self.slice_del():
                    return False

            elif among_var == 5:
                # (, line 142
                # call R2, line 142
                if not self.r_R2():
                    raise lab4()
                # Boolean test e_found, line 142
                if not self.B_e_found:
                    raise lab4()
                # delete, line 142
                if not self.slice_del():
                    return False

        except lab4: pass
        self.cursor = self.limit - v_5
        # do, line 146
        v_9 = self.limit - self.cursor
        try:
            # (, line 146
            if not self.out_grouping_b(DutchStemmer.g_v_I, 73, 232):
                raise lab9()
            # test, line 148
            v_10 = self.limit - self.cursor
            # (, line 148
            # among, line 149
            if self.find_among_b(DutchStemmer.a_5, 4) == 0:
                raise lab9()
            if not self.out_grouping_b(DutchStemmer.g_v, 97, 232):
                raise lab9()
            self.cursor = self.limit - v_10
            # [, line 152
            self.ket = self.cursor
            # next, line 152
            if self.cursor <= self.limit_backward:
                raise lab9()
            self.cursor -= 1
            # ], line 152
            self.bra = self.cursor
            # delete, line 152
            if not self.slice_del():
                return False

        except lab9: pass
        self.cursor = self.limit - v_9
        return True

    def _stem(self):
        # (, line 157
        # do, line 159
        v_1 = self.cursor
        try:
            # call prelude, line 159
            if not self.r_prelude():
                raise lab0()
        except lab0: pass
        self.cursor = v_1
        # do, line 160
        v_2 = self.cursor
        try:
            # call mark_regions, line 160
            if not self.r_mark_regions():
                raise lab1()
        except lab1: pass
        self.cursor = v_2
        # backwards, line 161
        self.limit_backward = self.cursor
        self.cursor = self.limit
        # do, line 162
        v_3 = self.limit - self.cursor
        try:
            # call standard_suffix, line 162
            if not self.r_standard_suffix():
                raise lab2()
        except lab2: pass
        self.cursor = self.limit - v_3
        self.cursor = self.limit_backward
        # do, line 163
        v_4 = self.cursor
        try:
            # call postlude, line 163
            if not self.r_postlude():
                raise lab3()
        except lab3: pass
        self.cursor = v_4
        return True

    def equals(self, o):
        return isinstance(o, DutchStemmer)

    def hashCode(self):
        return hash("DutchStemmer")
class lab0(BaseException): pass
class lab1(BaseException): pass
class lab2(BaseException): pass
class lab3(BaseException): pass
class lab4(BaseException): pass
class lab5(BaseException): pass
class lab6(BaseException): pass
class lab7(BaseException): pass
class lab8(BaseException): pass
class lab9(BaseException): pass
class lab10(BaseException): pass
