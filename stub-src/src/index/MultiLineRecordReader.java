package index;

import java.io.IOException;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileSplit;
import org.apache.hadoop.mapred.InputSplit;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.LineRecordReader;
import org.apache.hadoop.mapred.RecordReader;
import org.apache.hadoop.mapred.Reporter;

public class MultiLineRecordReader implements RecordReader<Text, Double[]> {

	private LineRecordReader lineReader;
	private LongWritable lineKey;
	private Text lineValue;
	private int size;

	public MultiLineRecordReader(JobConf job, FileSplit split)
			throws IOException {
		lineReader = new LineRecordReader(job, split);
		size = 100;
		lineKey = lineReader.createKey();
		lineValue = lineReader.createValue();
	}

	public boolean next(Text key, Double[] value) throws IOException {
		// get the next line

		for (int ct = 0; ct < size; ct++) {

			if (!lineReader.next(lineKey, lineValue)) {
				if (ct == 0){
					return false;
				}
				else{
					return true;
				}	
			}
			value[ct] = Double.valueOf(lineValue.toString());

		}

		return true;
	}

	public Text createKey() {
		return new Text("");
	}

	public Double[] createValue() {
		return new Double[size];
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
