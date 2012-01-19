
package proj;

import java.io.IOException;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;

/**
 * MinMapper
 *
 * Maps each observed word in a line to a (filename@offset) string.
 *
 * @author(tri1, corbin2)
 */
public class MinMapper extends MapReduceBase implements
		Mapper<LongWritable, Text, Text, DoubleWritable> {

	public MinMapper() { }

	public void map(LongWritable key, Text value,
			OutputCollector<Text, DoubleWritable> output, Reporter reporter)
			throws IOException, NumberFormatException {
		
		output.collect(new Text("cnt"), new DoubleWritable(1.0));
		output.collect(new Text("min"), new DoubleWritable(Double.valueOf(value.toString()).doubleValue()));
	}
}
