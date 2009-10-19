package proj;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

public class MedianCalculator {

	// finds median of 5 elements
	public static Double getMedian(ArrayList<Double> theValues) {

		Double retVal = 0.0;
		Collections.sort(theValues);

		switch (theValues.size()) {
		case 1:
			retVal = theValues.get(0);
			break;
		case 2:
			retVal = (theValues.get(0) + theValues.get(1)) / 2;
			break;
		case 3:
			retVal = theValues.get(1);
			break;
		case 4:
			retVal = (theValues.get(1) + theValues.get(2)) / 2;
			break;
		case 5:
			retVal = theValues.get(2);
			break;
		}

		return retVal;
	}

	// reduce list by finding median of each 5 elements
	public static ArrayList<Double> reduceList(ArrayList<Double> theValues) {

		// return values
		ArrayList<Double> aRetVal = new ArrayList<Double>();
		// holds 5 doubles to find median
		Double[] sortedFive = new Double[5];
		int fivePos = 0;

		// loops though all values passed in and makes list of medians
		for (int i = 0; i < theValues.size(); i++) {

			sortedFive[fivePos] = theValues.get(i);
			fivePos++;

			if (fivePos == 5) {
				fivePos = 0;
				Arrays.sort(sortedFive);
				aRetVal.add(sortedFive[2]);
			}

		}

		// handles leftover elements
		switch (fivePos) {
		case 1:
			aRetVal.add(sortedFive[0]);
			break;
		case 2:
			aRetVal.add((sortedFive[0] + sortedFive[1]) / 2);
			break;
		case 3:
			aRetVal.add(sortedFive[1]);
			break;
		case 4:
			aRetVal.add((sortedFive[1] + sortedFive[2]) / 2);
			break;
		}

		return aRetVal;
	}

}
