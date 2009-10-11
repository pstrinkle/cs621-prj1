
package index;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
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

		ArrayList<Double> sortedValues = new ArrayList<Double>();
		
		while (values.hasNext()) {
			sortedValues.add(values.next().get());
		}
		
		Collections.sort(sortedValues);
		//Arrays.sort(sortedValues.toArray());

		double cnt = values.size();
		double med = 0;

		if ((cnt % 2) == 0)
		{
			double x = value.get((int)(cnt / 2));
			double y = value.get((int)((cnt / 2) + 1));
			med = (x + y) / 2;
			// even
		}
		else
		{
			med = value.get((int)Math.ceil(cnt / 2));
			// odd
		}

		// make output
		
		
		
		output.collect(new Text(key), new DoubleWritable(med));
	}
}
