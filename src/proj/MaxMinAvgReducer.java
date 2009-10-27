
package proj;

import java.io.IOException;
import java.util.Iterator;
import java.util.StringTokenizer;

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
public class MaxMinAvgReducer extends MapReduceBase implements
		Reducer<Text, Text, Text, Text> {

	public MaxMinAvgReducer() {
	}

	public void reduce(Text key, Iterator<Text> values,
			OutputCollector<Text, Text> output, Reporter reporter)
			throws IOException {

		double max = 0;
		double min = 0;
		double result = 0;
		double current = 0;
		boolean first = true;

		// you could have the if statement in the while loop
		// but then you'd have to check the key at each iteration
		if (key.toString().equals("max")) {
			while (values.hasNext()) {

				current = Double.valueOf(values.next());

				if (first) {
					max = current;
				}

				if (current > max) {
					max = current;
				}

				first = false;
			}
			
			result = max;
		} else if (key.toString().equals("min")) {
			while (values.hasNext()) {

				current = Double.valueOf(values.next());

				if (first) {
					min = current;
				}

				if (current < min) {
					min = current;
				}

				first = false;
			}
			
			result = min;
		} else if (key.toString().equals("cnt")) {
			result = 0; // redundant
			
			while (values.hasNext()) {				
				result += Double.valueOf(values.next());
			}
		} else if (key.toString().equals("avg")) {
		
      double sum = 0;
			int cnt = 0;

			while (values.hasNext()) {

				StringTokenizer itr = new StringTokenizer(values.next().toString(), " ");

				if (itr.countTokens() == 2) {

					String newcnt = itr.nextToken();
					cnt += Double.valueOf(newcnt);

					String newsum = itr.nextToken();
					sum += Double.valueOf(newsum);
				} else {
					// too many tokens!
				}
			}
			
			result = sum / cnt;
    }
		output.collect(new Text(key), new Text(Double.toString(result)));
	}
}
