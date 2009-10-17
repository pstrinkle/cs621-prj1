
package proj;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;

/**
 * MaxMapper
 *
 * Maps each observed word in a line to a (filename@offset) string.
 *
 * @author(tri1, corbin2)
 */
public class MaxMinMapper extends MapReduceBase implements
		Mapper<LongWritable, ArrayList<Double>, Text, DoubleWritable> {

	public MaxMinMapper() {
	}

	public void map(LongWritable key, ArrayList<Double> value,
			OutputCollector<Text, DoubleWritable> output, Reporter reporter)
			throws IOException, NumberFormatException {

		// technically we could set the value equal to a local variable and
		// try/catch it if the
		// double is invalid--might be a better way to handle the error case.

		double max = 0, min = 0;
		boolean first = true;
		
		for (Double d : value) {
			if (first) {
				max = d;
				min = d;
			}
			
			if (d > max) {
				max = d;
			} else if (d < min) {
				min = d;
			}
			
			first = false;
		}

		output.collect(new Text("max"), new DoubleWritable(max));
		output.collect(new Text("min"), new DoubleWritable(min));
		output.collect(new Text("cnt"), new DoubleWritable(value.size()));
	}
}
