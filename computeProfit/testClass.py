class ClassA:
    member_A = 0
    list_A = []
    def __init__(self):
        self.selfmember_A = 1
        self.selflist_A = []
        self.selflist_A.append(1)
    def add(self, num):
        self.selfmember_A = num
        self.selflist_A.append(num)

A1 = ClassA()
print('-------A1 ori-------')
print(A1.member_A)
print(A1.list_A)
print(A1.selfmember_A)
print(A1.selflist_A)
A1.member_A = 2
A1.list_A.append(2)
A1.add(2)
print('-------A1 after A1 add 2-------')
print(A1.member_A)
print(A1.list_A)
print(A1.selfmember_A)
print(A1.selflist_A)
print('-------A2 after A1 add 2-------')
A2 = ClassA()
print(A2.member_A)
print(A2.list_A)
print(A2.selfmember_A)
print(A2.selflist_A)

A2.member_A = 3
A2.list_A.append(3)
A2.add(3)
print('-------A2 after A2 add 3-------')
print(A2.member_A)
print(A2.list_A)
print(A2.selfmember_A)
print(A2.selflist_A)
print('-------A1 after A2 add 3-------')
print(A1.member_A)
print(A1.list_A)
print(A1.selfmember_A)
print(A1.selflist_A)