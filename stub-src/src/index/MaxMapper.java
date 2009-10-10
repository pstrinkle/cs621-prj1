
package index;

import java.io.IOException;

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
public class MaxMapper extends MapReduceBase implements
		Mapper<LongWritable, Text, Text, DoubleWritable> {

	public MaxMapper() { }

	public void map(LongWritable key, Text value,
			OutputCollector<Text, DoubleWritable> output, Reporter reporter)
			throws IOException, NumberFormatException {

		// technically we could set the value equal to a local variable and try/catch it if the 
		// double is invalid--might be a better way to handle the error case.
		
		output.collect(new Text("max"), new DoubleWritable(Double.valueOf(value.toString()).doubleValue()));
	}
}
