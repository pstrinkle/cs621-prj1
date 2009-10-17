package proj;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reporter;

/**
 * AvgMapper
 * 
 * Maps each observed word in a line to a (filename@offset) string.
 * 
 * @author(tri1, corbin2)
 */
public class AvgMapper extends MapReduceBase implements
		Mapper<LongWritable, ArrayList<Double>, Text, Text> {

	public AvgMapper() {
	}

	public void map(LongWritable key, ArrayList<Double> value,
			OutputCollector<Text, Text> output, Reporter reporter)
			throws IOException, NumberFormatException {

		// in the old version this dumped (avg, value)
		
		StringBuilder outputline = new StringBuilder();

		int cnt = 0;
		double sum = 0;
		
		for (Double d: value) {
			sum += d;
		}

		cnt = value.size();
		
		// make output
		outputline.append(cnt);
		outputline.append(' ');
		outputline.append(sum);

		output.collect(new Text("avg"), new Text(outputline.toString()));
		output.collect(new Text("cnt"), new Text(Integer.toString(cnt)));
	}
}
