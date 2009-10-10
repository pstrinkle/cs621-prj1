// (c) Copyright 2009 Cloudera, Inc.

package index;

import static org.apache.hadoop.mrunit.testutil.ExtendedAssert.*;

import org.apache.hadoop.mrunit.ReduceDriver;
import org.apache.hadoop.mrunit.types.Pair;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import junit.framework.TestCase;

import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.Reducer;
import org.junit.Before;
import org.junit.Test;

/**
 * Test cases for the inverted index reducer.
 */
public class ReducerTest extends TestCase {

  private Reducer<Text, DoubleWritable, Text, Text> reducer;
  private ReduceDriver<Text, DoubleWritable, Text, Text> driver;

  @Before
  public void setUp() {
    reducer = new AvgReducer();
    driver = new ReduceDriver<Text, DoubleWritable, Text, Text>(reducer);
  }

  @Test
  public void testOneOffset() {
    List<Pair<Text, Text>> out = null;
  }

  @Test
  public void testMultiOffset() {
    List<Pair<Text, Text>> out = null;
  }

}

