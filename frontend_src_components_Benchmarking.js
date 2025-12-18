import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Spin, Table, Tag, Button } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { fetchBenchmarkingData } from '../services/api';

const { Option } = Select;

const Benchmarking = ({ selectedMonth }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [benchmarkType, setBenchmarkType] = useState('industry');
  const [industryData, setIndustryData] = useState(null);
  const [competitorData, setCompetitorData] = useState(null);
  const [historicalBenchmark, setHistoricalBenchmark] = useState(null);

  useEffect(() => {
    if (selectedMonth) {
      setLoading(true);
      fetchBenchmarkingData(selectedMonth, benchmarkType)
        .then(response => {
          setData(response.data);
          setIndustryData(response.data.industryData);
          setCompetitorData(response.data.competitorData);
          setHistoricalBenchmark(response.data.historicalBenchmark);
        })
        .catch(error => {
          console.error('Error fetching benchmarking data:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [selectedMonth, benchmarkType]);

  const industryColumns = [
    {
      title: 'Metric',
      dataIndex: 'metric',
      key: 'metric',
    },
    {
      title: 'Our Company',
      dataIndex: 'ourCompany',
      key: 'ourCompany',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Industry Average',
      dataIndex: 'industryAvg',
      key: 'industryAvg',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Top Quartile',
      dataIndex: 'topQuartile',
      key: 'topQuartile',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Performance',
      dataIndex: 'performance',
      key: 'performance',
      render: performance => (
        <Tag color={performance === 'Above Average' ? 'green' : performance === 'Average' ? 'orange' : 'red'}>
          {performance}
        </Tag>
      ),
    },
  ];

  const competitorColumns = [
    {
      title: 'Metric',
      dataIndex: 'metric',
      key: 'metric',
    },
    {
      title: 'Our Company',
      dataIndex: 'ourCompany',
      key: 'ourCompany',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Competitor A',
      dataIndex: 'competitorA',
      key: 'competitorA',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Competitor B',
      dataIndex: 'competitorB',
      key: 'competitorB',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Competitor C',
      dataIndex: 'competitorC',
      key: 'competitorC',
      render: value => (
        <Tag color={value >= 0 ? 'green' : 'red'}>
          {value >= 0 ? '+' : ''}{value}%
        </Tag>
      ),
    },
    {
      title: 'Ranking',
      dataIndex: 'ranking',
      key: 'ranking',
      render: ranking => (
        <Tag color={ranking === 1 ? 'green' : ranking === 2 ? 'orange' : 'red'}>
          #{ranking}
        </Tag>
      ),
    },
  ];

  if (loading || !data) {
    return <Spin size="large" />;
  }

  return (
    <div className="benchmarking">
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card title="Benchmarking Type">
            <Select
              value={benchmarkType}
              onChange={setBenchmarkType}
              style={{ width: 200, marginRight: 16 }}
            >
              <Option value="industry">Industry Benchmarking</Option>
              <Option value="competitor">Competitor Analysis</Option>
              <Option value="historical">Historical Performance</Option>
            </Select>
            <Button type="primary" onClick={() => window.print()}>
              Export to PDF
            </Button>
          </Card>
        </Col>
      </Row>

      {benchmarkType === 'industry' && (
        <>
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Industry Comparison - Margins">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={industryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="ourCompany" fill="#8884d8" name="Our Company" />
                    <Bar dataKey="industryAvg" fill="#82ca9d" name="Industry Average" />
                    <Bar dataKey="topQuartile" fill="#ffc658" name="Top Quartile" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Industry Comparison - Growth Rates">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={industryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="ourCompany" fill="#8884d8" name="Our Company" />
                    <Bar dataKey="industryAvg" fill="#82ca9d" name="Industry Average" />
                    <Bar dataKey="topQuartile" fill="#ffc658" name="Top Quartile" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Card title="Industry Benchmarking Details">
                <Table
                  columns={industryColumns}
                  dataSource={industryData}
                  pagination={{ pageSize: 10 }}
                  rowKey="metric"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {benchmarkType === 'competitor' && (
        <>
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Competitor Comparison - Margins">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={competitorData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="ourCompany" fill="#8884d8" name="Our Company" />
                    <Bar dataKey="competitorA" fill="#82ca9d" name="Competitor A" />
                    <Bar dataKey="competitorB" fill="#ffc658" name="Competitor B" />
                    <Bar dataKey="competitorC" fill="#ff7300" name="Competitor C" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Competitor Comparison - Growth Rates">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={competitorData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="ourCompany" fill="#8884d8" name="Our Company" />
                    <Bar dataKey="competitorA" fill="#82ca9d" name="Competitor A" />
                    <Bar dataKey="competitorB" fill="#ffc658" name="Competitor B" />
                    <Bar dataKey="competitorC" fill="#ff7300" name="Competitor C" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Card title="Competitor Analysis Details">
                <Table
                  columns={competitorColumns}
                  dataSource={competitorData}
                  pagination={{ pageSize: 10 }}
                  rowKey="metric"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {benchmarkType === 'historical' && (
        <>
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Historical Performance - Margins">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historicalBenchmark}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Line type="monotone" dataKey="gpm" stroke="#8884d8" name="Gross Profit Margin" />
                    <Line type="monotone" dataKey="opm" stroke="#82ca9d" name="Operating Profit Margin" />
                    <Line type="monotone" dataKey="npm" stroke="#ffc658" name="Net Profit Margin" />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Historical Performance - Growth Rates">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historicalBenchmark}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Line type="monotone" dataKey="revenueGrowth" stroke="#8884d8" name="Revenue Growth" />
                    <Line type="monotone" dataKey="profitGrowth" stroke="#82ca9d" name="Profit Growth" />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Performance Radar">
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={historicalBenchmark.slice(-1)}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar name="Current Month" dataKey="current" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    <Radar name="Previous Month" dataKey="previous" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Year-over-Year Comparison">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={historicalBenchmark.slice(-12)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="yoyRevenueGrowth" fill="#8884d8" name="YoY Revenue Growth" />
                    <Bar dataKey="yoyProfitGrowth" fill="#82ca9d" name="YoY Profit Growth" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Card title="Historical Performance Details">
                <Table
                  columns={[
                    {
                      title: 'Month',
                      dataIndex: 'month',
                      key: 'month',
                    },
                    {
                      title: 'Revenue',
                      dataIndex: 'revenue',
                      key: 'revenue',
                      render: revenue => `$${revenue.toLocaleString()}`,
                    },
                    {
                      title: 'Revenue Growth',
                      dataIndex: 'revenueGrowth',
                      key: 'revenueGrowth',
                      render: growth => (
                        <Tag color={growth >= 0 ? 'green' : 'red'}>
                          {growth >= 0 ? '+' : ''}{growth}%
                        </Tag>
                      ),
                    },
                    {
                      title: 'Gross Profit Margin',
                      dataIndex: 'gpm',
                      key: 'gpm',
                      render: gpm => (
                        <Tag color={gpm < 20 ? 'red' : gpm < 30 ? 'orange' : 'green'}>
                          {gpm}%
                        </Tag>
                      ),
                    },
                    {
                      title: 'Operating Profit Margin',
                      dataIndex: 'opm',
                      key: 'opm',
                      render: opm => (
                        <Tag color={opm < 5 ? 'red' : opm < 10 ? 'orange' : 'green'}>
                          {opm}%
                        </Tag>
                      ),
                    },
                    {
                      title: 'Net Profit Margin',
                      dataIndex: 'npm',
                      key: 'npm',
                      render: npm => (
                        <Tag color={npm < 5 ? 'red' : npm < 10 ? 'orange' : 'green'}>
                          {npm}%
                        </Tag>
                      ),
                    },
                  ]}
                  dataSource={historicalBenchmark}
                  pagination={{ pageSize: 12 }}
                  rowKey="month"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}
    </div>
  );
};

export default Benchmarking;