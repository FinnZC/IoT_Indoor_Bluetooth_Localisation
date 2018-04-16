#https://www.kdnuggets.com/2017/02/removing-outliers-standard-deviation-python.html
import numpy

arr = [-101, -101, -101, -101]

elements = numpy.array(arr)
mean = numpy.mean(elements, axis=0)
sd = numpy.std(elements, axis=0)

final_list = [x for x in arr if (x >= mean - 2 * sd)]
final_list = [x for x in final_list if (x <= mean + 2 * sd)]

print(final_list)
print(numpy.mean(final_list))
