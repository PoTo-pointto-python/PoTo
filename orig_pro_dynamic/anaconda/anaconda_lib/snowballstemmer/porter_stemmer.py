# self file was generated automatically by the Snowball to Python interpreter

from .basestemmer import BaseStemmer
from .among import Among


class PorterStemmer(BaseStemmer):
    '''
    self class was automatically generated by a Snowball to Python interpreter
    It implements the stemming algorithm defined by a snowball script.
    '''
    serialVersionUID = 1

    a_0 = [
        Among(u"s", -1, 3),
        Among(u"ies", 0, 2),
        Among(u"sses", 0, 1),
        Among(u"ss", 0, -1)
    ]

    a_1 = [
        Among(u"", -1, 3),
        Among(u"bb", 0, 2),
        Among(u"dd", 0, 2),
        Among(u"ff", 0, 2),
        Among(u"gg", 0, 2),
        Among(u"bl", 0, 1),
        Among(u"mm", 0, 2),
        Among(u"nn", 0, 2),
        Among(u"pp", 0, 2),
        Among(u"rr", 0, 2),
        Among(u"at", 0, 1),
        Among(u"tt", 0, 2),
        Among(u"iz", 0, 1)
    ]

    a_2 = [
        Among(u"ed", -1, 2),
        Among(u"eed", 0, 1),
        Among(u"ing", -1, 2)
    ]

    a_3 = [
        Among(u"anci", -1, 3),
        Among(u"enci", -1, 2),
        Among(u"abli", -1, 4),
        Among(u"eli", -1, 6),
        Among(u"alli", -1, 9),
        Among(u"ousli", -1, 12),
        Among(u"entli", -1, 5),
        Among(u"aliti", -1, 10),
        Among(u"biliti", -1, 14),
        Among(u"iviti", -1, 13),
        Among(u"tional", -1, 1),
        Among(u"ational", 10, 8),
        Among(u"alism", -1, 10),
        Among(u"ation", -1, 8),
        Among(u"ization", 13, 7),
        Among(u"izer", -1, 7),
        Among(u"ator", -1, 8),
        Among(u"iveness", -1, 13),
        Among(u"fulness", -1, 11),
        Among(u"ousness", -1, 12)
    ]

    a_4 = [
        Among(u"icate", -1, 2),
        Among(u"ative", -1, 3),
        Among(u"alize", -1, 1),
        Among(u"iciti", -1, 2),
        Among(u"ical", -1, 2),
        Among(u"ful", -1, 3),
        Among(u"ness", -1, 3)
    ]

    a_5 = [
        Among(u"ic", -1, 1),
        Among(u"ance", -1, 1),
        Among(u"ence", -1, 1),
        Among(u"able", -1, 1),
        Among(u"ible", -1, 1),
        Among(u"ate", -1, 1),
        Among(u"ive", -1, 1),
        Among(u"ize", -1, 1),
        Among(u"iti", -1, 1),
        Among(u"al", -1, 1),
        Among(u"ism", -1, 1),
        Among(u"ion", -1, 2),
        Among(u"er", -1, 1),
        Among(u"ous", -1, 1),
        Among(u"ant", -1, 1),
        Among(u"ent", -1, 1),
        Among(u"ment", 15, 1),
        Among(u"ement", 16, 1),
        Among(u"ou", -1, 1)
    ]

    g_v = [17, 65, 16, 1]

    g_v_WXY = [1, 17, 65, 208, 1]

    B_Y_found = False
    I_p2 = 0
    I_p1 = 0

    def copy_from(self, other):
        self.B_Y_found = other.B_Y_found
        self.I_p2 = other.I_p2
        self.I_p1 = other.I_p1
        super.copy_from(other)
    

    def r_shortv(self):
        # (, line 19
        if not self.out_grouping_b(PorterStemmer.g_v_WXY, 89, 121):
            return False
        if not self.in_grouping_b(PorterStemmer.g_v, 97, 121):
            return False
        if not self.out_grouping_b(PorterStemmer.g_v, 97, 121):
            return False
        return True

    def r_R1(self):
        if not self.I_p1 <= self.cursor:
            return False
        return True

    def r_R2(self):
        if not self.I_p2 <= self.cursor:
            return False
        return True

    def r_Step_1a(self):
        # (, line 24
        # [, line 25
        self.ket = self.cursor
        # substring, line 25
        among_var = self.find_among_b(PorterStemmer.a_0, 4)
        if among_var == 0:
            return False
        # ], line 25
        self.bra = self.cursor
        if among_var == 0:
            return False
        elif among_var == 1:
            # (, line 26
            # <-, line 26
            if not self.slice_from(u"ss"):
                return False
        elif among_var == 2:
            # (, line 27
            # <-, line 27
            if not self.slice_from(u"i"):
                return False
        elif among_var == 3:
            # (, line 29
            # delete, line 29
            if not self.slice_del():
                return False

        return True

    def r_Step_1b(self):
        # (, line 33
        # [, line 34
        self.ket = self.cursor
        # substring, line 34
        among_var = self.find_among_b(PorterStemmer.a_2, 3)
        if among_var == 0:
            return False
        # ], line 34
        self.bra = self.cursor
        if among_var == 0:
            return False
        elif among_var == 1:
            # (, line 35
            # call R1, line 35
            if not self.r_R1():
                return False
            # <-, line 35
            if not self.slice_from(u"ee"):
                return False
        elif among_var == 2:
            # (, line 37
            # test, line 38
            v_1 = self.limit - self.cursor
            # gopast, line 38
            try:
                while True:
                    try:
                        if not self.in_grouping_b(PorterStemmer.g_v, 97, 121):
                            raise lab1()
                        raise lab0()
                    except lab1: pass
                    if self.cursor <= self.limit_backward:
                        return False
                    self.cursor -= 1
            except lab0: pass
            self.cursor = self.limit - v_1
            # delete, line 38
            if not self.slice_del():
                return False

            # test, line 39
            v_3 = self.limit - self.cursor
            # substring, line 39
            among_var = self.find_among_b(PorterStemmer.a_1, 13)
            if among_var == 0:
                return False
            self.cursor = self.limit - v_3
            if among_var == 0:
                return False
            elif among_var == 1:
                # (, line 41
                # <+, line 41
                c = self.cursor
                self.insert(self.cursor, self.cursor, u"e")
                self.cursor = c
            elif among_var == 2:
                # (, line 44
                # [, line 44
                self.ket = self.cursor
                # next, line 44
                if self.cursor <= self.limit_backward:
                    return False
                self.cursor -= 1
                # ], line 44
                self.bra = self.cursor
                # delete, line 44
                if not self.slice_del():
                    return False

            elif among_var == 3:
                # (, line 45
                # atmark, line 45
                if self.cursor != self.I_p1:
                    return False
                # test, line 45
                v_4 = self.limit - self.cursor
                # call shortv, line 45
                if not self.r_shortv():
                    return False
                self.cursor = self.limit - v_4
                # <+, line 45
                c = self.cursor
                self.insert(self.cursor, self.cursor, u"e")
                self.cursor = c
        return True

    def r_Step_1c(self):
        # (, line 51
        # [, line 52
        self.ket = self.cursor
        # or, line 52
        try:
            v_1 = self.limit - self.cursor
            try:
                # literal, line 52
                if not self.eq_s_b(1, u"y"):
                    raise lab1()
                raise lab0()
            except lab1: pass
            self.cursor = self.limit - v_1
            # literal, line 52
            if not self.eq_s_b(1, u"Y"):
                return False
        except lab0: pass
        # ], line 52
        self.bra = self.cursor
        # gopast, line 53
        try:
            while True:
                try:
                    if not self.in_grouping_b(PorterStemmer.g_v, 97, 121):
                        raise lab3()
                    raise lab2()
                except lab3: pass
                if self.cursor <= self.limit_backward:
                    return False
                self.cursor -= 1
        except lab2: pass
        # <-, line 54
        if not self.slice_from(u"i"):
            return False
        return True

    def r_Step_2(self):
        # (, line 57
        # [, line 58
        self.ket = self.cursor
        # substring, line 58
        among_var = self.find_among_b(PorterStemmer.a_3, 20)
        if among_var == 0:
            return False
        # ], line 58
        self.bra = self.cursor
        # call R1, line 58
        if not self.r_R1():
            return False
        if among_var == 0:
            return False
        elif among_var == 1:
            # (, line 59
            # <-, line 59
            if not self.slice_from(u"tion"):
                return False
        elif among_var == 2:
            # (, line 60
            # <-, line 60
            if not self.slice_from(u"ence"):
                return False
        elif among_var == 3:
            # (, line 61
            # <-, line 61
            if not self.slice_from(u"ance"):
                return False
        elif among_var == 4:
            # (, line 62
            # <-, line 62
            if not self.slice_from(u"able"):
                return False
        elif among_var == 5:
            # (, line 63
            # <-, line 63
            if not self.slice_from(u"ent"):
                return False
        elif among_var == 6:
            # (, line 64
            # <-, line 64
            if not self.slice_from(u"e"):
                return False
        elif among_var == 7:
            # (, line 66
            # <-, line 66
            if not self.slice_from(u"ize"):
                return False
        elif among_var == 8:
            # (, line 68
            # <-, line 68
            if not self.slice_from(u"ate"):
                return False
        elif among_var == 9:
            # (, line 69
            # <-, line 69
            if not self.slice_from(u"al"):
                return False
        elif among_var == 10:
            # (, line 71
            # <-, line 71
            if not self.slice_from(u"al"):
                return False
        elif among_var == 11:
            # (, line 72
            # <-, line 72
            if not self.slice_from(u"ful"):
                return False
        elif among_var == 12:
            # (, line 74
            # <-, line 74
            if not self.slice_from(u"ous"):
                return False
        elif among_var == 13:
            # (, line 76
            # <-, line 76
            if not self.slice_from(u"ive"):
                return False
        elif among_var == 14:
            # (, line 77
            # <-, line 77
            if not self.slice_from(u"ble"):
                return False
        return True

    def r_Step_3(self):
        # (, line 81
        # [, line 82
        self.ket = self.cursor
        # substring, line 82
        among_var = self.find_among_b(PorterStemmer.a_4, 7)
        if among_var == 0:
            return False
        # ], line 82
        self.bra = self.cursor
        # call R1, line 82
        if not self.r_R1():
            return False
        if among_var == 0:
            return False
        elif among_var == 1:
            # (, line 83
            # <-, line 83
            if not self.slice_from(u"al"):
                return False
        elif among_var == 2:
            # (, line 85
            # <-, line 85
            if not self.slice_from(u"ic"):
                return False
        elif among_var == 3:
            # (, line 87
            # delete, line 87
            if not self.slice_del():
                return False

        return True

    def r_Step_4(self):
        # (, line 91
        # [, line 92
        self.ket = self.cursor
        # substring, line 92
        among_var = self.find_among_b(PorterStemmer.a_5, 19)
        if among_var == 0:
            return False
        # ], line 92
        self.bra = self.cursor
        # call R2, line 92
        if not self.r_R2():
            return False
        if among_var == 0:
            return False
        elif among_var == 1:
            # (, line 95
            # delete, line 95
            if not self.slice_del():
                return False

        elif among_var == 2:
            # (, line 96
            # or, line 96
            try:
                v_1 = self.limit - self.cursor
                try:
                    # literal, line 96
                    if not self.eq_s_b(1, u"s"):
                        raise lab1()
                    raise lab0()
                except lab1: pass
                self.cursor = self.limit - v_1
                # literal, line 96
                if not self.eq_s_b(1, u"t"):
                    return False
            except lab0: pass
            # delete, line 96
            if not self.slice_del():
                return False

        return True

    def r_Step_5a(self):
        # (, line 100
        # [, line 101
        self.ket = self.cursor
        # literal, line 101
        if not self.eq_s_b(1, u"e"):
            return False
        # ], line 101
        self.bra = self.cursor
        # or, line 102
        try:
            v_1 = self.limit - self.cursor
            try:
                # call R2, line 102
                if not self.r_R2():
                    raise lab1()
                raise lab0()
            except lab1: pass
            self.cursor = self.limit - v_1
            # (, line 102
            # call R1, line 102
            if not self.r_R1():
                return False
            # not, line 102
            v_2 = self.limit - self.cursor
            try:
                # call shortv, line 102
                if not self.r_shortv():
                    raise lab2()
                return False
            except lab2: pass
            self.cursor = self.limit - v_2
        except lab0: pass
        # delete, line 103
        if not self.slice_del():
            return False

        return True

    def r_Step_5b(self):
        # (, line 106
        # [, line 107
        self.ket = self.cursor
        # literal, line 107
        if not self.eq_s_b(1, u"l"):
            return False
        # ], line 107
        self.bra = self.cursor
        # call R2, line 108
        if not self.r_R2():
            return False
        # literal, line 108
        if not self.eq_s_b(1, u"l"):
            return False
        # delete, line 109
        if not self.slice_del():
            return False

        return True

    def _stem(self):
        # (, line 113
        # unset Y_found, line 115
        self.B_Y_found = False
        # do, line 116
        v_1 = self.cursor
        try:
            # (, line 116
            # [, line 116
            self.bra = self.cursor
            # literal, line 116
            if not self.eq_s(1, u"y"):
                raise lab0()
            # ], line 116
            self.ket = self.cursor
            # <-, line 116
            if not self.slice_from(u"Y"):
                return False
            # set Y_found, line 116
            self.B_Y_found = True
        except lab0: pass
        self.cursor = v_1
        # do, line 117
        v_2 = self.cursor
        try:
            # repeat, line 117
            try:
                while True:
                    try:
                        v_3 = self.cursor
                        try:
                            # (, line 117
                            # goto, line 117
                            try:
                                while True:
                                    v_4 = self.cursor
                                    try:
                                        # (, line 117
                                        if not self.in_grouping(PorterStemmer.g_v, 97, 121):
                                            raise lab6()
                                        # [, line 117
                                        self.bra = self.cursor
                                        # literal, line 117
                                        if not self.eq_s(1, u"y"):
                                            raise lab6()
                                        # ], line 117
                                        self.ket = self.cursor
                                        self.cursor = v_4
                                        raise lab5()
                                    except lab6: pass
                                    self.cursor = v_4
                                    if self.cursor >= self.limit:
                                        raise lab4()
                                    self.cursor += 1
                            except lab5: pass
                            # <-, line 117
                            if not self.slice_from(u"Y"):
                                return False
                            # set Y_found, line 117
                            self.B_Y_found = True
                            raise lab3()
                        except lab4: pass
                        self.cursor = v_3
                        raise lab2()
                    except lab3: pass
            except lab2: pass
        except lab1: pass
        self.cursor = v_2
        self.I_p1 = self.limit;
        self.I_p2 = self.limit;
        # do, line 121
        v_5 = self.cursor
        try:
            # (, line 121
            # gopast, line 122
            try:
                while True:
                    try:
                        if not self.in_grouping(PorterStemmer.g_v, 97, 121):
                            raise lab9()
                        raise lab8()
                    except lab9: pass
                    if self.cursor >= self.limit:
                        raise lab7()
                    self.cursor += 1
            except lab8: pass
            # gopast, line 122
            try:
                while True:
                    try:
                        if not self.out_grouping(PorterStemmer.g_v, 97, 121):
                            raise lab11()
                        raise lab10()
                    except lab11: pass
                    if self.cursor >= self.limit:
                        raise lab7()
                    self.cursor += 1
            except lab10: pass
            # setmark p1, line 122
            self.I_p1 = self.cursor
            # gopast, line 123
            try:
                while True:
                    try:
                        if not self.in_grouping(PorterStemmer.g_v, 97, 121):
                            raise lab13()
                        raise lab12()
                    except lab13: pass
                    if self.cursor >= self.limit:
                        raise lab7()
                    self.cursor += 1
            except lab12: pass
            # gopast, line 123
            try:
                while True:
                    try:
                        if not self.out_grouping(PorterStemmer.g_v, 97, 121):
                            raise lab15()
                        raise lab14()
                    except lab15: pass
                    if self.cursor >= self.limit:
                        raise lab7()
                    self.cursor += 1
            except lab14: pass
            # setmark p2, line 123
            self.I_p2 = self.cursor
        except lab7: pass
        self.cursor = v_5
        # backwards, line 126
        self.limit_backward = self.cursor
        self.cursor = self.limit
        # (, line 126
        # do, line 127
        v_10 = self.limit - self.cursor
        try:
            # call Step_1a, line 127
            if not self.r_Step_1a():
                raise lab16()
        except lab16: pass
        self.cursor = self.limit - v_10
        # do, line 128
        v_11 = self.limit - self.cursor
        try:
            # call Step_1b, line 128
            if not self.r_Step_1b():
                raise lab17()
        except lab17: pass
        self.cursor = self.limit - v_11
        # do, line 129
        v_12 = self.limit - self.cursor
        try:
            # call Step_1c, line 129
            if not self.r_Step_1c():
                raise lab18()
        except lab18: pass
        self.cursor = self.limit - v_12
        # do, line 130
        v_13 = self.limit - self.cursor
        try:
            # call Step_2, line 130
            if not self.r_Step_2():
                raise lab19()
        except lab19: pass
        self.cursor = self.limit - v_13
        # do, line 131
        v_14 = self.limit - self.cursor
        try:
            # call Step_3, line 131
            if not self.r_Step_3():
                raise lab20()
        except lab20: pass
        self.cursor = self.limit - v_14
        # do, line 132
        v_15 = self.limit - self.cursor
        try:
            # call Step_4, line 132
            if not self.r_Step_4():
                raise lab21()
        except lab21: pass
        self.cursor = self.limit - v_15
        # do, line 133
        v_16 = self.limit - self.cursor
        try:
            # call Step_5a, line 133
            if not self.r_Step_5a():
                raise lab22()
        except lab22: pass
        self.cursor = self.limit - v_16
        # do, line 134
        v_17 = self.limit - self.cursor
        try:
            # call Step_5b, line 134
            if not self.r_Step_5b():
                raise lab23()
        except lab23: pass
        self.cursor = self.limit - v_17
        self.cursor = self.limit_backward
        # do, line 137
        v_18 = self.cursor
        try:
            # (, line 137
            # Boolean test Y_found, line 137
            if not self.B_Y_found:
                raise lab24()
            # repeat, line 137
            try:
                while True:
                    try:
                        v_19 = self.cursor
                        try:
                            # (, line 137
                            # goto, line 137
                            try:
                                while True:
                                    v_20 = self.cursor
                                    try:
                                        # (, line 137
                                        # [, line 137
                                        self.bra = self.cursor
                                        # literal, line 137
                                        if not self.eq_s(1, u"Y"):
                                            raise lab29()
                                        # ], line 137
                                        self.ket = self.cursor
                                        self.cursor = v_20
                                        raise lab28()
                                    except lab29: pass
                                    self.cursor = v_20
                                    if self.cursor >= self.limit:
                                        raise lab27()
                                    self.cursor += 1
                            except lab28: pass
                            # <-, line 137
                            if not self.slice_from(u"y"):
                                return False
                            raise lab26()
                        except lab27: pass
                        self.cursor = v_19
                        raise lab25()
                    except lab26: pass
            except lab25: pass
        except lab24: pass
        self.cursor = v_18
        return True

    def equals(self, o):
        return isinstance(o, PorterStemmer)

    def hashCode(self):
        return hash("PorterStemmer")
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
class lab11(BaseException): pass
class lab12(BaseException): pass
class lab13(BaseException): pass
class lab14(BaseException): pass
class lab15(BaseException): pass
class lab16(BaseException): pass
class lab17(BaseException): pass
class lab18(BaseException): pass
class lab19(BaseException): pass
class lab20(BaseException): pass
class lab21(BaseException): pass
class lab22(BaseException): pass
class lab23(BaseException): pass
class lab24(BaseException): pass
class lab25(BaseException): pass
class lab26(BaseException): pass
class lab27(BaseException): pass
class lab28(BaseException): pass
class lab29(BaseException): pass
