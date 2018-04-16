#https://www.kdnuggets.com/2017/02/removing-outliers-standard-deviation-python.html
import numpy

arr = [61,
66,
76,
62,
76,
62,
66,
76,
62,
62,
75,
62,
67,
65,
74,
62,
75,
62,
67,
74,
63,
67,
74,
62,
66,
74,
62,
67,
62,
66,
74,
61,
76,
62,
66,
62,
66,
62,
66,
74,
62,
62,
66,
74,
64,
66,
74,
62,
65,
62,
65
]

elements = numpy.array(arr)
mean = numpy.mean(elements, axis=0)
sd = numpy.std(elements, axis=0)

final_list = [x for x in arr if (x > mean - 2 * sd)]
final_list = [x for x in final_list if (x < mean + 2 * sd)]

print(final_list)
print(numpy.mean(final_list))
