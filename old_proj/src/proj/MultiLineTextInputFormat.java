
package proj;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileSplit;
import org.apache.hadoop.mapred.InputSplit;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.RecordReader;
import org.apache.hadoop.mapred.Reporter;

public class MultiLineTextInputFormat extends FileInputFormat<LongWritable, ArrayList<Double>> {

	public RecordReader<LongWritable, ArrayList<Double>> getRecordReader(InputSplit input,
			JobConf job, Reporter reporter) throws IOException {

		reporter.setStatus(input.toString());

		return new MultiLineRecordReader(job, (FileSplit) input);
	}
}
