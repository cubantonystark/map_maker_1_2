import cv2

# Load the image
filepath = 'C:/Users/micha/Documents/PhotogrammetryDataSets/house_test3/DJI_0002.jpg'

img = cv2.imread(filepath)

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Load the car classifier
car_classifier = cv2.CascadeClassifier('cars.xml')

# Detect the cars in the image
cars = car_classifier.detectMultiScale(gray, 1.1, 5)

# Draw rectangles around the cars
for (x, y, w, h) in cars:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

# Display the image
cv2.imshow('Cars Detected', img)
cv2.waitKey(0)
cv2.destroyAllWindows()