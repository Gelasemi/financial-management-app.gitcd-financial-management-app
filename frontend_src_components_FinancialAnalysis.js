import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Spin, Table, Tag, Button } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { fetchAnalysisData } from '../services/api';

const { Option } = Select;

const FinancialAnalysis = ({ selectedMonth }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisType, setAnalysisType] = useState('cost');
  const [costBreakdown, setCostBreakdown] = useState(null);
  const [revenueBreakdown, setRevenueBreakdown] = useState(null);
  const [profitabilityAnalysis, setProfitabilityAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  useEffect(() => {
    if (selectedMonth) {
      setLoading(true);
      fetchAnalysisData(selectedMonth, analysisType)
        .then(response => {
          setData(response.data);
          setCostBreakdown(response.data.costBreakdown);
          setRevenueBreakdown(response.data.revenueBreakdown);
          setProfitabilityAnalysis(response.data.profitabilityAnalysis);
          setRecommendations(response.data.recommendations);
        })
        .catch(error => {
          console.error('Error fetching analysis data:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [selectedMonth, analysisType]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const costColumns = [
    {
      title: 'Cost Category',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: amount => `$${amount.toLocaleString()}`,
      sorter: (a, b) => a.amount - b.amount,
    },
    {
      title: '% of Total',
      dataIndex: 'percentage',
      key: 'percentage',
      render: percentage => `${percentage}%`,
      sorter: (a, b) => a.percentage - b.percentage,
    },
    {
      title: 'Trend',
      dataIndex: 'trend',
      key: 'trend',
      render: trend => (
        <Tag color={trend > 0 ? 'red' : 'green'}>
          {trend > 0 ? '+' : ''}{trend}% vs last month
        </Tag>
      ),
    },
  ];

  const revenueColumns = [
    {
      title: 'Revenue Source',
      dataIndex: 'source',
      key: 'source',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: amount => `$${amount.toLocaleString()}`,
      sorter: (a, b) => a.amount - b.amount,
    },
    {
      title: '% of Total',
      dataIndex: 'percentage',
      key: 'percentage',
      render: percentage => `${percentage}%`,
      sorter: (a, b) => a.percentage - b.percentage,
    },
    {
      title: 'Trend',
      dataIndex: 'trend',
      key: 'trend',
      render: trend => (
        <Tag color={trend > 0 ? 'green' : 'red'}>
          {trend > 0 ? '+' : ''}{trend}% vs last month
        </Tag>
      ),
    },
  ];

  if (loading || !data) {
    return <Spin size="large" />;
  }

  return (
    <div className="financial-analysis">
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={24}>
          <Card title="Analysis Type">
            <Select
              value={analysisType}
              onChange={setAnalysisType}
              style={{ width: 200, marginRight: 16 }}
            >
              <Option value="cost">Cost Analysis</Option>
              <Option value="revenue">Revenue Analysis</Option>
              <Option value="profitability">Profitability Analysis</Option>
            </Select>
            <Button type="primary" onClick={() => window.print()}>
              Export to PDF
            </Button>
          </Card>
        </Col>
      </Row>

      {analysisType === 'cost' && (
        <>
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Cost Breakdown">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={costBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {costBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Cost Categories">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={costBreakdown}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                    <Bar dataKey="amount" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Card title="Cost Analysis Details">
                <Table
                  columns={costColumns}
                  dataSource={costBreakdown}
                  pagination={{ pageSize: 10 }}
                  rowKey="category"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {analysisType === 'revenue' && (
        <>
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Revenue Breakdown">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={revenueBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {revenueBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Revenue Sources">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={revenueBreakdown}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="source" />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                    <Bar dataKey="amount" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Card title="Revenue Analysis Details">
                <Table
                  columns={revenueColumns}
                  dataSource={revenueBreakdown}
                  pagination={{ pageSize: 10 }}
                  rowKey="source"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {analysisType === 'profitability' && (
        <>
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={12}>
              <Card title="Profitability Trend">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={profitabilityAnalysis}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="gpm" fill="#8884d8" name="Gross Profit Margin" />
                    <Bar dataKey="opm" fill="#82ca9d" name="Operating Profit Margin" />
                    <Bar dataKey="npm" fill="#ffc658" name="Net Profit Margin" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="Profitability Comparison">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={profitabilityAnalysis.slice(-6)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <Bar dataKey="gpm" fill="#8884d8" name="Gross Profit Margin" />
                    <Bar dataKey="opm" fill="#82ca9d" name="Operating Profit Margin" />
                    <Bar dataKey="npm" fill="#ffc658" name="Net Profit Margin" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Card title="Profitability Analysis">
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
                      title: 'Cost of Sales',
                      dataIndex: 'cost',
                      key: 'cost',
                      render: cost => `$${cost.toLocaleString()}`,
                    },
                    {
                      title: 'Gross Profit',
                      dataIndex: 'grossProfit',
                      key: 'grossProfit',
                      render: grossProfit => `$${grossProfit.toLocaleString()}`,
                    },
                    {
                      title: 'GPM',
                      dataIndex: 'gpm',
                      key: 'gpm',
                      render: gpm => (
                        <Tag color={gpm < 20 ? 'red' : gpm < 30 ? 'orange' : 'green'}>
                          {gpm}%
                        </Tag>
                      ),
                    },
                    {
                      title: 'Operating Profit',
                      dataIndex: 'operatingProfit',
                      key: 'operatingProfit',
                      render: operatingProfit => `$${operatingProfit.toLocaleString()}`,
                    },
                    {
                      title: 'OPM',
                      dataIndex: 'opm',
                      key: 'opm',
                      render: opm => (
                        <Tag color={opm < 5 ? 'red' : opm < 10 ? 'orange' : 'green'}>
                          {opm}%
                        </Tag>
                      ),
                    },
                    {
                      title: 'Net Profit',
                      dataIndex: 'netProfit',
                      key: 'netProfit',
                      render: netProfit => `$${netProfit.toLocaleString()}`,
                    },
                    {
                      title: 'NPM',
                      dataIndex: 'npm',
                      key: 'npm',
                      render: npm => (
                        <Tag color={npm < 5 ? 'red' : npm < 10 ? 'orange' : 'green'}>
                          {npm}%
                        </Tag>
                      ),
                    },
                  ]}
                  dataSource={profitabilityAnalysis}
                  pagination={{ pageSize: 12 }}
                  rowKey="month"
                />
              </Card>
            </Col>
          </Row>
        </>
      )}

      <Row gutter={16} style={{ marginTop: 20 }}>
        <Col span={24}>
          <Card title="Recommendations">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-card">
                <div className="recommendation-title">{rec.title}</div>
                <div className="recommendation-content">{rec.content}</div>
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default FinancialAnalysis;