import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, Spin, Table, Tag } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { fetchDashboardData } from '../services/api';

const { Option } = Select;

const Dashboard = ({ selectedMonth }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [kpiData, setKpiData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  const [entityData, setEntityData] = useState(null);
  const [redFlags, setRedFlags] = useState(null);

  useEffect(() => {
    if (selectedMonth) {
      setLoading(true);
      fetchDashboardData(selectedMonth)
        .then(response => {
          setData(response.data);
          setKpiData(response.data.kpi);
          setMonthlyData(response.data.monthly);
          setEntityData(response.data.entities);
          setRedFlags(response.data.redFlags);
        })
        .catch(error => {
          console.error('Error fetching dashboard data:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [selectedMonth]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const redFlagColumns = [
    {
      title: 'Project',
      dataIndex: 'project',
      key: 'project',
    },
    {
      title: 'Country',
      dataIndex: 'country',
      key: 'country',
    },
    {
      title: 'Gross Profit Margin',
      dataIndex: 'gpm',
      key: 'gpm',
      render: gpm => (
        <Tag color={gpm < 10 ? 'red' : gpm < 20 ? 'orange' : 'green'}>
          {gpm}%
        </Tag>
      ),
    },
    {
      title: 'Comment',
      dataIndex: 'comment',
      key: 'comment',
      ellipsis: true,
    },
  ];

  const entityColumns = [
    {
      title: 'Entity',
      dataIndex: 'entity',
      key: 'entity',
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
      dataIndex: 'gp',
      key: 'gp',
      render: gp => `$${gp.toLocaleString()}`,
    },
    {
      title: 'GP Margin',
      dataIndex: 'gpm',
      key: 'gpm',
      render: gpm => (
        <Tag color={gpm < 10 ? 'red' : gpm < 20 ? 'orange' : 'green'}>
          {gpm}%
        </Tag>
      ),
    },
  ];

  if (loading || !data) {
    return <Spin size="large" />;
  }

  return (
    <div className="dashboard">
      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={6}>
          <Card className="kpi-card">
            <div className="kpi-value">${kpiData?.revenue?.toLocaleString()}</div>
            <div className="kpi-label">Total Revenue</div>
            <div className={`kpi-change ${kpiData?.revenueChange >= 0 ? 'positive' : 'negative'}`}>
              {kpiData?.revenueChange >= 0 ? '+' : ''}{kpiData?.revenueChange}% vs last month
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="kpi-card">
            <div className="kpi-value">{kpiData?.gpm}%</div>
            <div className="kpi-label">Gross Profit Margin</div>
            <div className={`kpi-change ${kpiData?.gpmChange >= 0 ? 'positive' : 'negative'}`}>
              {kpiData?.gpmChange >= 0 ? '+' : ''}{kpiData?.gpmChange}% vs last month
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="kpi-card">
            <div className="kpi-value">${kpiData?.opex?.toLocaleString()}</div>
            <div className="kpi-label">Operating Expenses</div>
            <div className={`kpi-change ${kpiData?.opexChange <= 0 ? 'positive' : 'negative'}`}>
              {kpiData?.opexChange <= 0 ? '' : '+'}{kpiData?.opexChange}% vs last month
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="kpi-card">
            <div className="kpi-value">${kpiData?.netProfit?.toLocaleString()}</div>
            <div className="kpi-label">Net Profit</div>
            <div className={`kpi-change ${kpiData?.netProfitChange >= 0 ? 'positive' : 'negative'}`}>
              {kpiData?.netProfitChange >= 0 ? '+' : ''}{kpiData?.netProfitChange}% vs last month
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={12}>
          <Card title="Monthly Revenue & Profit Trend">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#8884d8" name="Revenue" />
                <Line type="monotone" dataKey="grossProfit" stroke="#82ca9d" name="Gross Profit" />
                <Line type="monotone" dataKey="netProfit" stroke="#ffc658" name="Net Profit" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Profit Margin Trend">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyData}>
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
      </Row>

      <Row gutter={16} style={{ marginBottom: 20 }}>
        <Col span={12}>
          <Card title="Entity Performance">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={entityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="entity" />
                <YAxis />
                <Tooltip formatter={(value) => `${value}%`} />
                <Legend />
                <Bar dataKey="gpm" fill="#8884d8" name="GP Margin" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Revenue by Entity">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={entityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="revenue"
                >
                  {entityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="Red Flags">
            <Table
              columns={redFlagColumns}
              dataSource={redFlags}
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Entity Details">
            <Table
              columns={entityColumns}
              dataSource={entityData}
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;