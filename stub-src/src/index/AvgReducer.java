package index;

import java.io.IOException;
import java.util.Iterator;
import java.util.StringTokenizer;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;

/**
 * AvgReducer
 * 
 * Takes a list of filename@offset entries for a single word and concatenates
 * them into a list.
 * 
 * @author(tri1, corbin2)
 */
public class AvgReducer extends MapReduceBase implements
		Reducer<Text, Text, Text, Text> {

	public AvgReducer() {
	}

	public void reduce(Text key, Iterator<Text> values,
			OutputCollector<Text, Text> output, Reporter reporter)
			throws IOException {

		if (key.toString().equals("avg")) {

			double sum = 0;
			int cnt = 0;

			while (values.hasNext()) {

				StringTokenizer itr = new StringTokenizer(values.next().toString(), " ");

				if (itr.countTokens() == 2) {

					String newcnt = itr.nextToken();
					cnt += Double.valueOf(newcnt);

					String newsum = itr.nextToken();
					sum += Double.valueOf(newsum);
				} else {
					// too many tokens!
				}
			}

			output.collect(new Text("avg"), new Text(Double.toString(sum / cnt)));
		} else if (key.toString().equals("cnt")) {

			int valuecnt = 0;

			while (values.hasNext()) {
				valuecnt += Integer.valueOf(values.next().toString());
			}

			output.collect(new Text("cnt"), new Text(Integer.toString(valuecnt)));
		}
	}
}

// Before it took in a DoubleWritable and just added the
// sum and the cnt stuff and then dumped out the value
