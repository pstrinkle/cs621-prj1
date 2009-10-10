
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
 * MinReducer
 *
 * Takes a list of filename@offset entries for a single word and concatenates
 * them into a list.
 *
 * @author(tri1, corbin2)
 */
public class MinReducer extends MapReduceBase implements
		Reducer<Text, DoubleWritable, Text, Text> {

	public MinReducer() { }

	public void reduce(Text key, Iterator<DoubleWritable> values,
			OutputCollector<Text, Text> output, Reporter reporter)
			throws IOException {

		double min = 0;
		double current;
		boolean first = true;

		while (values.hasNext()) {

			current = values.next().get();

			if (first) {
				min = current;
			}

			if (current < min) {
				min = current;
			}

			first = false;
		}

		output.collect(new Text("min"), new Text(Double.toString(min)));
	}
}

