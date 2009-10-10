
package index;

import java.io.IOException;

import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.util.ToolRunner;
import org.apache.hadoop.util.Tool;

/**
 * ProjectOne
 *
 * Creates an inverted index over all the words in a document corpus, mapping
 * each observed word to a list of filename@offset locations where it occurs.
 *
 * @author(tri1, corbin2)
 */
public class ProjectOne extends Configured implements Tool {

	// where to put the data in hdfs when we're done
	private static final String OUTPUT_PATH = "output";

	// where to read the data from.
	private static final String INPUT_PATH = "workspace";

	/** Driver for the actual MapReduce process */
	private void runJob(String type, String in, String out) throws IOException {
		JobConf conf = new JobConf(getConf(), ProjectOne.class);

		FileInputFormat.addInputPath(conf, new Path(in));
		FileOutputFormat.setOutputPath(conf, new Path(out));

		if (type.equals("max")) {
			conf.setMapperClass(MaxMapper.class);
			conf.setReducerClass(MaxReducer.class);
		} else if (type.equals("min")) {
			conf.setMapperClass(MinMapper.class);
			conf.setReducerClass(MaxReducer.class);
		} else if (type.equals("avg")) {
			conf.setMapperClass(AvgMapper.class);
			conf.setReducerClass(AvgReducer.class);
		} else if (type.equals("test")) {
			// it tests by running max
			conf.setInputFormat(MultiLineTextInputFormat.class);
			conf.setMapperClass(MaxMapper.class);
			conf.setReducerClass(MaxReducer.class);
		} else {
			System.console().printf("Currently unsupported: %s\n", type);
			return;
		}

		conf.setOutputKeyClass(Text.class);
		conf.setOutputValueClass(DoubleWritable.class);
		conf.setJobName("Value Processing");
		
		JobClient.runJob(conf);
	}

  	private boolean verifyArgs(String[] args) {
  		if (args.length != 1) {
  			return false;
  		}
  		
  		if (args[0].equals("test")) {
  			return true;
  		}
  		
  		if (args[0].equals("max") || args[0].equals("min")
  				|| args[0].equals("avg") || args[0].equals("med")) {
  			return true;
  		}
  		
  		return false;
  	}

	public int run(String[] args) throws IOException {
		System.console().printf("Input Path: %s\n", INPUT_PATH);
		System.console().printf("Output Path: %s\n", OUTPUT_PATH);

		if (verifyArgs(args)) {
			runJob(args[0], INPUT_PATH, OUTPUT_PATH);
		} else {
			System.console().printf("usage: ... must provide max, min, avg\n");
			System.exit(-1);
		}

		return 0;
	}

	public static void main(String[] args) throws Exception {
		int ret = ToolRunner.run(new ProjectOne(), args);
		System.exit(ret);
	}
}
