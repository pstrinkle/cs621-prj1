package proj;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

/**
 * MaxReducer
 * 
 * Takes a list of filename@offset entries for a single word and concatenates
 * them into a list.
 * 
 * @author(tri1, corbin2)
 */
public class MedianReducer extends MapReduceBase implements
		Reducer<Text, DoubleWritable, Text, DoubleWritable> {

	public MedianReducer() {
	}
	
	public void reduce(Text key, Iterator<DoubleWritable> values,
			OutputCollector<Text, DoubleWritable> output, Reporter reporter)
			throws IOException {

		double result = 0;

		if (key.toString().equals("med")) {
			// reduce init input
			Double[] sortedFive = new Double[5];
			ArrayList<Double> sortedValues = new ArrayList<Double>();

			int fivePos = 0;
			while (values.hasNext()) {
				sortedFive[fivePos] = values.next().get();

				fivePos++;
					
				if (fivePos == 5) {
					fivePos = 0;
					Arrays.sort(sortedFive);
					// save the median
					sortedValues.add(sortedFive[2]);
				}
			}
			// handle left overs, not sure if should find the median here or
			// just add numbers to end of list

			// if there's less than 5 medians left... we can just tack them on?

			switch (fivePos) {
			case 1:
				sortedValues.add(sortedFive[0]);
				break;
			case 2:
				sortedValues.add((sortedFive[0] + sortedFive[1]) / 2);
				break;
			case 3:
				sortedValues.add(sortedFive[1]);
				break;
			case 4:
				sortedValues.add((sortedFive[1] + sortedFive[2]) / 2);
				break;
			}

			// reduce list down to last 5 numbers
			while (sortedValues.size() > 5) {
				sortedValues = MedianCalculator.reduceList(sortedValues);
			}

			result = MedianCalculator.getMedian(sortedValues);
			
		} else if (key.toString().equals("cnt")) {
			while (values.hasNext()) {
				result += values.next().get();
			}
		}

		// make output
		output.collect(new Text(key), new DoubleWritable(result));
	}
}
