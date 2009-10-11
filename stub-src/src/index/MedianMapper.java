package index;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

import org.apache.hadoop.io.DoubleWritable;
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
public class MedianMapper extends MapReduceBase implements
		Mapper<LongWritable, ArrayList<Double>, Text, DoubleWritable> {

	public MedianMapper() {
	}

	public void map(LongWritable key, ArrayList<Double> value,
			OutputCollector<Text, DoubleWritable> output, Reporter reporter)
			throws IOException, NumberFormatException {

		// in the old version this dumped (avg, value)
		Collections.sort(value);

		double cnt = value.size();
		double med = 0;
		
		if (cnt > 1) {

			if ((cnt % 2) == 0) {
				double x = value.get((int) (cnt / 2));
				double y = value.get((int) ((cnt / 2) + 1));
				med = (x + y) / 2;
				// even
			} else {
				med = value.get((int) Math.ceil(cnt / 2));
				// odd
			}
		} else {
			med = value.get(0);
		}

		// make output
		
		output.collect(new Text("med"), new DoubleWritable(med));
		output.collect(new Text("cnt"), new DoubleWritable(cnt));
	}
}
