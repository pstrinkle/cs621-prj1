
package proj;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileSplit;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.LineRecordReader;
import org.apache.hadoop.mapred.RecordReader;

public class MultiLineRecordReader implements RecordReader<LongWritable, ArrayList<Double>> {

	private LineRecordReader lineReader;
	private LongWritable lineKey;
	private Text lineValue;
	private int size;

	public MultiLineRecordReader(JobConf job, FileSplit split)
			throws IOException {
		lineReader = new LineRecordReader(job, split);
		size = 1000;
		lineKey = lineReader.createKey();
		lineValue = lineReader.createValue();
	}

	public boolean next(LongWritable key, ArrayList<Double> value) throws IOException,
			NumberFormatException {
		
		value.clear();
		// get the next line
		
		// if the first line is the length then the lineKey being set to 0 is something
		// we'd just skip
		for (int ct = 0; ct < size; ct++) {
			
			if (!lineReader.next(lineKey, lineValue)) {
				if (ct == 0) {
					return false;
				} else {
					return true;
				}
			}
			
			value.add(Double.valueOf(lineValue.toString()));
		}

		return true;
	}

	public LongWritable createKey() {
		return new LongWritable();
	}

	public ArrayList<Double> createValue() {
		return new ArrayList<Double>();
	}

	public long getPos() throws IOException {
		return lineReader.getPos();
	}

	public void close() throws IOException {
		lineReader.close();
	}

	public float getProgress() throws IOException {
		return lineReader.getProgress();
	}
}
