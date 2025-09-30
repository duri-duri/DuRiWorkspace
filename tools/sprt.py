import math
class SPRT:
    def __init__(self, p0=0.98, p1=0.995, alpha=0.05, beta=0.05):
        self.A = math.log((1-beta)/alpha)
        self.B = math.log(beta/(1-alpha))
        self.p0, self.p1 = p0, p1
        self.llr = 0.0
    def step(self, success): # success: 1 if pass golden
        p1 = self.p1 if success else (1-self.p1)
        p0 = self.p0 if success else (1-self.p0)
        self.llr += math.log(p1/p0)
        if self.llr >= self.A: return "accept"
        if self.llr <= self.B: return "reject"
        return "continue"


