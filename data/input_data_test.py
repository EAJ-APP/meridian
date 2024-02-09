# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl.testing import absltest
from absl.testing import parameterized
from meridian import constants
from meridian.data import input_data
from meridian.data import test_utils
import xarray as xr


class InputDataTest(parameterized.TestCase):

  def setUp(self):
    """Generates `sample` DataArrays."""
    super().setUp()

    self.n_times = 149
    self.n_lagged_media_times = 152
    self.n_geos = 10
    self.n_media_channels = 6
    self.n_rf_channels = 2
    self.n_controls = 3

    self.not_lagged_media = test_utils.random_media_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_times,
        n_media_channels=self.n_media_channels,
    )
    self.not_lagged_media_invalid_time_values = test_utils.random_media_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_times,
        n_media_channels=self.n_media_channels,
        date_format="week-%U",
    )
    self.lagged_media = test_utils.random_media_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_lagged_media_times,
        n_media_channels=self.n_media_channels,
    )
    self.media_spend = test_utils.random_media_spend_nd_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_channels=self.n_media_channels,
    )
    self.media_spend_1d = test_utils.random_media_spend_nd_da(
        n_media_channels=self.n_media_channels
    )
    self.not_lagged_controls = test_utils.random_controls_da(
        media=self.not_lagged_media,
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_controls=self.n_controls,
    )
    self.not_lagged_controls_invalid_time_values = (
        test_utils.random_controls_da(
            media=self.not_lagged_media,
            n_geos=self.n_geos,
            n_times=self.n_times,
            n_controls=self.n_controls,
            date_format="week-%U",
        )
    )
    self.lagged_controls = test_utils.random_controls_da(
        media=self.lagged_media,
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_controls=self.n_controls,
    )
    self.not_lagged_kpi = test_utils.random_kpi_da(
        media=self.not_lagged_media,
        controls=self.not_lagged_controls,
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_channels=self.n_media_channels,
        n_controls=self.n_controls,
    )
    self.lagged_kpi = test_utils.random_kpi_da(
        media=self.lagged_media,
        controls=self.lagged_controls,
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_channels=self.n_media_channels,
        n_controls=self.n_controls,
    )
    self.revenue_per_kpi = test_utils.constant_revenue_per_kpi(
        n_geos=self.n_geos, n_times=self.n_times, value=2.2
    )
    self.population = test_utils.random_population(n_geos=self.n_geos)
    self.not_lagged_reach = test_utils.random_reach_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_times,
        n_rf_channels=self.n_rf_channels,
    )
    self.lagged_reach = test_utils.random_reach_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_lagged_media_times,
        n_rf_channels=self.n_rf_channels,
    )
    self.not_lagged_frequency = test_utils.random_frequency_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_times,
        n_rf_channels=self.n_rf_channels,
    )
    self.lagged_frequency = test_utils.random_frequency_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_times=self.n_lagged_media_times,
        n_rf_channels=self.n_rf_channels,
    )
    self.rf_spend = test_utils.random_rf_spend_nd_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_rf_channels=self.n_rf_channels,
    )

  def test_construct_media_only_invalid_media_time_values(self):
    with self.assertRaisesRegex(
        ValueError, expected_regex="Invalid media_time label: week-04"
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media_invalid_time_values,
          media_spend=self.media_spend,
      )

  def test_construct_media_only_invalid_controls_time_values(self):
    with self.assertRaisesRegex(
        ValueError, expected_regex="Invalid time label: week-04"
    ):
      input_data.InputData(
          controls=self.not_lagged_controls_invalid_time_values,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media,
          media_spend=self.media_spend,
      )

  def test_construct_from_random_dataarrays_media_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
    )

    xr.testing.assert_equal(data.kpi, self.not_lagged_kpi)
    xr.testing.assert_equal(data.revenue_per_kpi, self.revenue_per_kpi)
    xr.testing.assert_equal(data.controls, self.not_lagged_controls)
    xr.testing.assert_equal(data.population, self.population)
    xr.testing.assert_equal(data.media, self.not_lagged_media)
    xr.testing.assert_equal(data.media_spend, self.media_spend)
    self.assertIsNone(data.reach)
    self.assertIsNone(data.frequency)
    self.assertIsNone(data.rf_spend)

  def test_construct_from_random_dataarrays_rf_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )

    xr.testing.assert_equal(data.kpi, self.not_lagged_kpi)
    xr.testing.assert_equal(data.revenue_per_kpi, self.revenue_per_kpi)
    xr.testing.assert_equal(data.controls, self.not_lagged_controls)
    xr.testing.assert_equal(data.population, self.population)
    xr.testing.assert_equal(data.reach, self.not_lagged_reach)
    xr.testing.assert_equal(data.frequency, self.not_lagged_frequency)
    xr.testing.assert_equal(data.rf_spend, self.rf_spend)
    self.assertIsNone(data.media)
    self.assertIsNone(data.media_spend)

  def test_construct_from_random_dataarrays_media_and_rf(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )

    xr.testing.assert_equal(data.kpi, self.not_lagged_kpi)
    xr.testing.assert_equal(data.revenue_per_kpi, self.revenue_per_kpi)
    xr.testing.assert_equal(data.media, self.not_lagged_media)
    xr.testing.assert_equal(data.media_spend, self.media_spend)
    xr.testing.assert_equal(data.controls, self.not_lagged_controls)
    xr.testing.assert_equal(data.population, self.population)
    xr.testing.assert_equal(data.reach, self.not_lagged_reach)
    xr.testing.assert_equal(data.frequency, self.not_lagged_frequency)
    xr.testing.assert_equal(data.rf_spend, self.rf_spend)

  def test_properties_media_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
    )

    xr.testing.assert_equal(data.geo, self.not_lagged_kpi[constants.GEO])
    xr.testing.assert_equal(
        data.time, self.not_lagged_kpi[constants.TIME]
    )
    xr.testing.assert_equal(
        data.media_time, self.not_lagged_media[constants.MEDIA_TIME]
    )
    xr.testing.assert_equal(
        data.media_channel, self.not_lagged_media[constants.MEDIA_CHANNEL]
    )
    xr.testing.assert_equal(
        data.control_variable,
        self.not_lagged_controls[constants.CONTROL_VARIABLE],
    )
    self.assertIsNone(data.rf_channel)

  def test_properties_rf_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )

    xr.testing.assert_equal(data.geo, self.not_lagged_kpi[constants.GEO])
    xr.testing.assert_equal(
        data.time, self.not_lagged_kpi[constants.TIME]
    )
    xr.testing.assert_equal(
        data.media_time, self.not_lagged_reach[constants.MEDIA_TIME]
    )
    xr.testing.assert_equal(
        data.rf_channel, self.not_lagged_reach[constants.RF_CHANNEL]
    )
    xr.testing.assert_equal(
        data.control_variable,
        self.not_lagged_controls[constants.CONTROL_VARIABLE],
    )
    self.assertIsNone(data.media_channel)

  def test_properties_media_and_rf(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )

    xr.testing.assert_equal(data.geo, self.not_lagged_kpi[constants.GEO])
    xr.testing.assert_equal(
        data.time, self.not_lagged_kpi[constants.TIME]
    )
    xr.testing.assert_equal(
        data.media_time, self.not_lagged_media[constants.MEDIA_TIME]
    )
    xr.testing.assert_equal(
        data.media_channel, self.not_lagged_media[constants.MEDIA_CHANNEL]
    )
    xr.testing.assert_equal(
        data.rf_channel, self.not_lagged_reach[constants.RF_CHANNEL]
    )
    xr.testing.assert_equal(
        data.control_variable,
        self.not_lagged_controls[constants.CONTROL_VARIABLE],
    )

  @parameterized.named_parameters(
      dict(testcase_name="geo_time_channel", n_geos=10, n_times=100),
      dict(testcase_name="channel", n_geos=None, n_times=None),
  )
  def test_spend_properties(self, n_geos: int | None, n_times: int | None):
    media_spend = test_utils.random_media_spend_nd_da(
        n_geos=n_geos, n_times=n_times, n_media_channels=self.n_media_channels
    )
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=media_spend,
    )
    self.assertEqual(n_geos is not None, data.media_spend_has_geo_dimension)
    self.assertEqual(n_times is not None, data.media_spend_has_time_dimension)
    self.assertFalse(data.rf_spend_has_geo_dimension)
    self.assertFalse(data.rf_spend_has_time_dimension)

  @parameterized.named_parameters(
      dict(testcase_name="geo_time_channel", n_geos=10, n_times=100),
      dict(testcase_name="channel", n_geos=None, n_times=None),
      dict(testcase_name="geo_channel", n_geos=10, n_times=None),
  )
  def test_rf_spend_properties(self, n_geos: int | None, n_times: int | None):
    rf_spend = test_utils.random_rf_spend_nd_da(
        n_geos=n_geos, n_times=n_times, n_rf_channels=self.n_rf_channels
    )
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=rf_spend,
    )
    self.assertEqual(n_geos is not None, data.rf_spend_has_geo_dimension)
    self.assertEqual(n_times is not None, data.rf_spend_has_time_dimension)
    self.assertFalse(data.media_spend_has_geo_dimension)
    self.assertFalse(data.media_spend_has_time_dimension)

  def test_construct_from_random_dataarrays_lagged(self):
    data = input_data.InputData(
        controls=self.lagged_controls,
        kpi=self.lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.lagged_media,
        media_spend=self.media_spend,
        reach=self.lagged_reach,
        frequency=self.lagged_frequency,
        rf_spend=self.rf_spend,
    )

    xr.testing.assert_equal(data.kpi, self.lagged_kpi)
    xr.testing.assert_equal(data.revenue_per_kpi, self.revenue_per_kpi)
    xr.testing.assert_equal(data.media, self.lagged_media)
    xr.testing.assert_equal(data.media_spend, self.media_spend)
    xr.testing.assert_equal(data.controls, self.lagged_controls)
    xr.testing.assert_equal(data.population, self.population)
    xr.testing.assert_equal(data.reach, self.lagged_reach)
    xr.testing.assert_equal(data.frequency, self.lagged_frequency)
    xr.testing.assert_equal(data.rf_spend, self.rf_spend)

  def test_construct_from_random_dataarrays_media_spend_1d(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend_1d,
    )

    xr.testing.assert_equal(data.kpi, self.not_lagged_kpi)
    xr.testing.assert_equal(data.revenue_per_kpi, self.revenue_per_kpi)
    xr.testing.assert_equal(data.media, self.not_lagged_media)
    xr.testing.assert_equal(data.media_spend, self.media_spend_1d)
    xr.testing.assert_equal(data.controls, self.not_lagged_controls)
    xr.testing.assert_equal(data.population, self.population)

  def test_as_dataset_media_and_rf(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )

    dataset = data.as_dataset()

    xr.testing.assert_equal(
        dataset[constants.KPI], self.not_lagged_kpi
    )
    xr.testing.assert_equal(
        dataset[constants.REVENUE_PER_KPI], self.revenue_per_kpi
    )
    xr.testing.assert_equal(dataset[constants.MEDIA], self.not_lagged_media)
    xr.testing.assert_equal(dataset[constants.MEDIA_SPEND], self.media_spend)
    xr.testing.assert_equal(
        dataset[constants.CONTROLS], self.not_lagged_controls
    )
    xr.testing.assert_equal(dataset[constants.POPULATION], self.population)
    xr.testing.assert_equal(dataset[constants.REACH], self.not_lagged_reach)
    xr.testing.assert_equal(
        dataset[constants.FREQUENCY], self.not_lagged_frequency
    )
    xr.testing.assert_equal(dataset[constants.RF_SPEND], self.rf_spend)

  def test_as_dataset_media_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
    )

    dataset = data.as_dataset()

    xr.testing.assert_equal(
        dataset[constants.KPI], self.not_lagged_kpi
    )
    xr.testing.assert_equal(
        dataset[constants.REVENUE_PER_KPI], self.revenue_per_kpi
    )
    xr.testing.assert_equal(
        dataset[constants.CONTROLS], self.not_lagged_controls
    )
    xr.testing.assert_equal(dataset[constants.POPULATION], self.population)
    xr.testing.assert_equal(dataset[constants.MEDIA], self.not_lagged_media)
    xr.testing.assert_equal(dataset[constants.MEDIA_SPEND], self.media_spend)
    self.assertNotIn(constants.REACH, dataset)
    self.assertNotIn(constants.FREQUENCY, dataset)
    self.assertNotIn(constants.RF_SPEND, dataset)

  def test_as_dataset_rf_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )

    dataset = data.as_dataset()

    xr.testing.assert_equal(
        dataset[constants.KPI], self.not_lagged_kpi
    )
    xr.testing.assert_equal(
        dataset[constants.REVENUE_PER_KPI], self.revenue_per_kpi
    )
    xr.testing.assert_equal(
        dataset[constants.CONTROLS], self.not_lagged_controls
    )
    xr.testing.assert_equal(dataset[constants.POPULATION], self.population)
    xr.testing.assert_equal(dataset[constants.REACH], self.not_lagged_reach)
    xr.testing.assert_equal(
        dataset[constants.FREQUENCY], self.not_lagged_frequency
    )
    xr.testing.assert_equal(dataset[constants.RF_SPEND], self.rf_spend)
    self.assertNotIn(constants.MEDIA, dataset)
    self.assertNotIn(constants.MEDIA_SPEND, dataset)

  def test_wrong_coordinate_name(self):
    media2 = self.not_lagged_media.rename({constants.GEO: "group"})

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        (
            "The dimension list of array 'media' doesn't match any of the"
            " following dimension lists: [['geo', 'media_time',"
            " 'media_channel']]."
        ),
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=media2,
          media_spend=self.media_spend,
      )

  def test_not_matching_dimensions(self):
    media_spend2 = test_utils.random_media_spend_nd_da(
        n_geos=self.n_geos,
        n_times=self.n_times,
        n_media_channels=self.n_media_channels - 1,
    )

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        "'media_channel' dimensions [6, 5] of arrays ['media', 'media_spend']"
        " don't match.",
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media,
          media_spend=media_spend2,
      )

  def test_not_matching_dimensions_media_spend_1d(self):
    media_spend_1d_2 = test_utils.random_media_spend_nd_da(
        n_media_channels=self.n_media_channels - 1
    )

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        "'media_channel' dimensions [6, 5] of arrays ['media', 'media_spend']"
        " don't match.",
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media,
          media_spend=media_spend_1d_2,
      )

  def test_media_spend_2d_fails(self):
    media_spend_2d = test_utils.random_media_spend_nd_da(
        n_geos=self.n_geos, n_media_channels=self.n_media_channels
    )

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        (
            "The dimension list of array 'media_spend' doesn't match any of the"
            " following dimension lists: [['media_channel'], ['geo', 'time',"
            " 'media_channel']]."
        ),
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media,
          media_spend=media_spend_2d,
      )

  def test_media_shorter_than_kpi_fails(self):
    media_short = self.not_lagged_media[
        :, (self.n_times - self.n_times + 1) :, :
    ]

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        (
            "The 'media_time' dimension of the 'media' array (148) cannot be"
            " smaller than the 'time' dimension of the 'kpi' array (149)"
        ),
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=media_short,
          media_spend=self.media_spend,
      )

  def test_reach_shorter_than_kpi_fails(self):
    reach_short = self.not_lagged_reach[
        :, (self.n_times - self.n_times + 1) :, :
    ]

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        (
            "The 'media_time' dimension of the 'reach' array (148) cannot be"
            " smaller than the 'time' dimension of the 'kpi' array (149)"
        ),
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media,
          media_spend=self.media_spend,
          reach=reach_short,
          frequency=self.not_lagged_frequency,
          rf_spend=self.rf_spend,
      )

  def test_frequency_shorter_than_kpi_fails(self):
    frequency_short = self.not_lagged_frequency[
        :, (self.n_times - self.n_times + 1) :, :
    ]

    with self.assertRaisesWithLiteralMatch(
        ValueError,
        (
            "The 'media_time' dimension of the 'frequency' array (148) cannot"
            " be smaller than the 'time' dimension of the 'kpi' array"
            " (149)"
        ),
    ):
      input_data.InputData(
          controls=self.not_lagged_controls,
          kpi=self.not_lagged_kpi,
          revenue_per_kpi=self.revenue_per_kpi,
          population=self.population,
          media=self.not_lagged_media,
          media_spend=self.media_spend,
          reach=self.not_lagged_reach,
          frequency=frequency_short,
      )

  def test_get_n_top_largest_geos(self):
    population = xr.DataArray(
        data=[100, 5, 50, 10, 75, 25, 80, 30, 20, 95],
        coords={constants.GEO: test_utils._sample_names(constants.GEO, 10)},
        name=constants.POPULATION,
    )
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
    )

    top_geos = data.get_n_top_largest_geos(3)
    self.assertEqual(top_geos, ["geo0", "geo9", "geo6"])

    top_geos = data.get_n_top_largest_geos(5)
    self.assertEqual(top_geos, ["geo0", "geo9", "geo6", "geo4", "geo2"])

  def test_get_all_channels_media_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        media=self.not_lagged_media,
        media_spend=self.media_spend,
    )
    channels = data.get_all_channels()
    self.assertTrue(
        (channels == self.not_lagged_media[constants.MEDIA_CHANNEL]).all()
    )

  def test_get_all_channels_rf_only(self):
    data = input_data.InputData(
        controls=self.not_lagged_controls,
        kpi=self.not_lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.not_lagged_reach,
        frequency=self.not_lagged_frequency,
        rf_spend=self.rf_spend,
    )
    channels = data.get_all_channels()
    self.assertTrue(
        (channels == self.not_lagged_reach[constants.RF_CHANNEL]).all()
    )

  def test_get_all_channels_media_and_rf(self):
    data = input_data.InputData(
        media=self.lagged_media,
        media_spend=self.media_spend,
        controls=self.lagged_controls,
        kpi=self.lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.lagged_reach,
        frequency=self.lagged_frequency,
        rf_spend=self.rf_spend,
    )
    channels = data.get_all_channels()
    self.assertLen(
        channels,
        self.n_media_channels + self.n_rf_channels,
    )
    self.assertTrue(
        channel in channels
        for channel in self.lagged_media[constants.MEDIA_CHANNEL]
    )
    self.assertTrue(
        channel in channels
        for channel in self.lagged_reach[constants.RF_CHANNEL]
    )

  def test_get_all_media_and_rf(self):
    data = input_data.InputData(
        media=self.lagged_media,
        media_spend=self.media_spend,
        controls=self.lagged_controls,
        kpi=self.lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.lagged_reach,
        frequency=self.lagged_frequency,
        rf_spend=self.rf_spend,
    )
    all_media_and_rf = data.get_all_media_and_rf()
    self.assertEqual(
        all_media_and_rf.shape,
        (
            self.n_geos,
            self.n_lagged_media_times,
            self.n_media_channels + self.n_rf_channels,
        ),
    )

    media_from_rf = self.lagged_reach * self.lagged_frequency
    self.assertTrue(media in all_media_and_rf for media in media_from_rf)
    self.assertTrue(media in all_media_and_rf for media in self.lagged_media)

  def test_get_all_spend(self):
    data = input_data.InputData(
        media=self.lagged_media,
        media_spend=self.media_spend,
        controls=self.lagged_controls,
        kpi=self.lagged_kpi,
        revenue_per_kpi=self.revenue_per_kpi,
        population=self.population,
        reach=self.lagged_reach,
        frequency=self.lagged_frequency,
        rf_spend=self.rf_spend,
    )
    total_spend = data.get_total_spend()
    self.assertEqual(
        total_spend.shape,
        (
            self.n_geos,
            self.n_times,
            self.n_media_channels + self.n_rf_channels,
        ),
    )
    self.assertTrue(spend in total_spend for spend in self.rf_spend)
    self.assertTrue(spend in total_spend for spend in self.media_spend)


if __name__ == "__main__":
  absltest.main()
