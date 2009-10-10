// (c) Copyright 2009 Cloudera, Inc.

package index;

import static org.apache.hadoop.mrunit.testutil.ExtendedAssert.*;

import org.apache.hadoop.mrunit.MapDriver;
import org.apache.hadoop.mrunit.mock.MockInputSplit;
import org.apache.hadoop.mrunit.types.Pair;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import junit.framework.TestCase;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.Mapper;
import org.junit.Before;
import org.junit.Test;

/**
 * Test cases for the inverted index mapper.
 */
public class MapperTest extends TestCase {

  private Mapper<LongWritable, Text, Text, DoubleWritable> mapper;
  private MapDriver<LongWritable, Text, Text, DoubleWritable> driver;

  /** We expect pathname@offset for the key from each of these */
  private final Text EXPECTED_OFFSET = new Text(MockInputSplit.getMockPath().toString() + "@0");

  @Before
  public void setUp() {
  }

  @Test
  public void testEmpty() {
    List<Pair<Text, Text>> out = null;
  }


  @Test
  public void testOneWord() {
    List<Pair<Text, Text>> out = null;
  }

  @Test
  public void testMultiWords() {
    List<Pair<Text, Text>> out = null;
  }

}

