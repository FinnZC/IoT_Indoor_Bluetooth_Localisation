print("55.944412, -3.186559")

timestamp = "yyyy-MM-dd 15:20:11.111"
hourMinuteSecondMillisecondReference = timestamp.split(" ")[1].split(":")
print(hourMinuteSecondMillisecondReference)

totalSecondsReference = float(hourMinuteSecondMillisecondReference[2]) \
               + float(hourMinuteSecondMillisecondReference[1])*60 \
               + float(hourMinuteSecondMillisecondReference[0])*60*60

print(totalSecondsReference)


a = {
    1 : "ts",
    4 : "asd",
    -1 : "afa",
    5 : "asd"
}
print(a)
print(sorted(a)[:3])

lst = list()
lst.append("213")
lst.append("asdas")

for item in lst:
    print(item)