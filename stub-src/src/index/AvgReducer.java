
package index;

import java.io.IOException;
import java.util.Iterator;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

/**
 * AvgReducer
 *
 * Takes a list of filename@offset entries for a single word and concatenates
 * them into a list.
 *
 * @author(tri1, corbin2)
 */
public class AvgReducer extends MapReduceBase implements
		Reducer<Text, DoubleWritable, Text, Text> {

	public AvgReducer() { }

	public void reduce(Text key, Iterator<DoubleWritable> values,
			OutputCollector<Text, Text> output, Reporter reporter)
			throws IOException {

		double sum = 0;
		int cnt = 0;

		while (values.hasNext()) {
			sum += values.next().get();
			cnt += 1;
		}

		output.collect(new Text("avg"), new Text(Double.toString(sum/cnt)));
	}
}

