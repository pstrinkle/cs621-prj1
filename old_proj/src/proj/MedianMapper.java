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

		int cnt = value.size();

		//reduces list down to 5 elements
		while (value.size()>5){
			value = MedianCalculator.reduceList(value);
		}

		output.collect(new Text("med"), new DoubleWritable(MedianCalculator.getMedian(value)));
		output.collect(new Text("cnt"), new DoubleWritable(cnt));
	}
}
