import React, { useState, useEffect } from 'react';
import { Card, Select, Button, Row, Col, Slider, Switch, Spin, Tabs } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea } from 'recharts';
import { fetchPredictionData } from '../services/api';

const { Option } = Select;
const { TabPane } = Tabs;

const PredictionModule = ({ selectedMonth }) => {
  const [predictionData, setPredictionData] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [target, setTarget] = useState('revenue');
  const [periods, setPeriods] = useState(6);
  const [modelType, setModelType] = useState('xgboost');
  const [scenario, setScenario] = useState('baseline');
  const [loading, setLoading] = useState(false);
  const [confidenceInterval, setConfidenceInterval] = useState(true);
  const [featureImportance, setFeatureImportance] = useState({});
  const [modelMetrics, setModelMetrics] = useState({});
  const [predictions, setPredictions] = useState({});
  const [activeTab, setActiveTab] = useState('1');

  useEffect(() => {
    if (selectedMonth) {
      fetchHistoricalData();
    }
  }, [selectedMonth, target]);

  const fetchHistoricalData = async () => {
    try {
      const response = await fetch(`/api/data/pnl?target=${target}&month=${selectedMonth}`);
      const data = await response.json();
      setHistoricalData(data);
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  };

  const generatePredictions = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/predict/pnl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target,
          periods,
          model_type: modelType,
          scenario,
          month: selectedMonth
        }),
      });
      const data = await response.json();
      
      // Combiner données historiques et prédictions
      const combinedData = [
        ...historicalData,
        ...data.predictions.map((value, index) => ({
          month: `Predicted ${index + 1}`,
          [target]: value,
          lower: confidenceInterval ? data.confidence_intervals[index][0] : null,
          upper: confidenceInterval ? data.confidence_intervals[index][1] : null,
          isPrediction: true
        }))
      ];
      
      setPredictionData(combinedData);
      setFeatureImportance(data.feature_importance || {});
      setModelMetrics(data.model_metrics || {});
      
      // Stocker les prédictions pour les autres onglets
      setPredictions({
        combinedData,
        featureImportance: data.feature_importance || {},
        modelMetrics: data.model_metrics || {}
      });
    } catch (error) {
      console.error('Error generating predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderCustomizedDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload.isPrediction) {
      return (
        <circle cx={cx} cy={cy} r={4} fill="#8884d8" />
      );
    }
    return null;
  };

  const renderFeatureImportance = () => {
    if (!Object.keys(featureImportance).length) return null;
    
    return (
      <Card title="Feature Importance" size="small">
        {Object.entries(featureImportance)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([feature, importance]) => (
            <div key={feature} style={{ marginBottom: 8 }}>
              <span>{feature}:</span>
              <span style={{ float: 'right' }}>{importance.toFixed(4)}</span>
            </div>
          ))}
      </Card>
    );
  };

  const renderModelMetrics = () => {
    if (!Object.keys(modelMetrics).length) return null;
    
    return (
      <Card title="Model Performance" size="small">
        <p>R²: {modelMetrics.r2_score?.toFixed(4)}</p>
        <p>MAE: {modelMetrics.mae?.toFixed(2)}</p>
        <p>RMSE: {modelMetrics.rmse?.toFixed(2)}</p>
      </Card>
    );
  };

  const renderScenarios = () => {
    if (!predictions.combinedData) return null;
    
    // Extraire les données de prédiction
    const predictionOnly = predictions.combinedData.filter(item => item.isPrediction);
    
    // Créer des données pour différents scénarios
    const scenariosData = predictionOnly.map((item, index) => {
      const baseValue = item[target];
      return {
        month: item.month,
        Baseline: baseValue,
        Optimistic: baseValue * 1.1,
        Pessimistic: baseValue * 0.9,
        Lower: item.lower,
        Upper: item.upper
      };
    });
    
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={scenariosData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
          <Legend />
          <Line type="monotone" dataKey="Baseline" stroke="#8884d8" strokeWidth={2} />
          <Line type="monotone" dataKey="Optimistic" stroke="#82ca9d" strokeWidth={2} strokeDasharray="5 5" />
          <Line type="monotone" dataKey="Pessimistic" stroke="#ff7300" strokeWidth={2} strokeDasharray="5 5" />
          {confidenceInterval && (
            <>
              <Line type="monotone" dataKey="Upper" stroke="#8884d8" strokeDasharray="3 3" dot={false} />
              <Line type="monotone" dataKey="Lower" stroke="#8884d8" strokeDasharray="3 3" dot={false} />
            </>
          )}
        </LineChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="prediction-module">
      <Card title="Financial Predictions" className="prediction-card">
        <Row gutter={16} style={{ marginBottom: 20 }}>
          <Col span={6}>
            <label>Target Metric:</label>
            <Select value={target} onChange={setTarget} style={{ width: '100%' }}>
              <Option value="revenue">Revenue</Option>
              <Option value="costs">Costs</Option>
              <Option value="gross_profit">Gross Profit</Option>
              <Option value="net_profit">Net Profit</Option>
            </Select>
          </Col>
          <Col span={6}>
            <label>Prediction Periods:</label>
            <Slider
              min={1}
              max={12}
              value={periods}
              onChange={setPeriods}
              marks={{
                1: '1',
                3: '3',
                6: '6',
                9: '9',
                12: '12'
              }}
            />
          </Col>
          <Col span={6}>
            <label>Model Type:</label>
            <Select value={modelType} onChange={setModelType} style={{ width: '100%' }}>
              <Option value="arima">ARIMA</Option>
              <Option value="xgboost">XGBoost</Option>
              <Option value="lstm">LSTM</Option>
              <Option value="prophet">Prophet</Option>
            </Select>
          </Col>
          <Col span={6}>
            <label>Scenario:</label>
            <Select value={scenario} onChange={setScenario} style={{ width: '100%' }}>
              <Option value="baseline">Baseline</Option>
              <Option value="optimistic">Optimistic</Option>
              <Option value="pessimistic">Pessimistic</Option>
            </Select>
          </Col>
        </Row>
        
        <Row gutter={16} style={{ marginBottom: 20 }}>
          <Col span={12}>
            <Switch
              checked={confidenceInterval}
              onChange={setConfidenceInterval}
            /> Show Confidence Interval
          </Col>
          <Col span={12}>
            <Button type="primary" onClick={generatePredictions} loading={loading}>
              Generate Predictions
            </Button>
          </Col>
        </Row>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Predictions" key="1">
            {predictionData.length > 0 && (
              <Row gutter={16}>
                <Col span={18}>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={predictionData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey={target} 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        dot={renderCustomizedDot}
                      />
                      {confidenceInterval && (
                        <>
                          <Line 
                            type="monotone" 
                            dataKey="upper" 
                            stroke="#8884d8" 
                            strokeDasharray="5 5"
                            dot={false}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="lower" 
                            stroke="#8884d8" 
                            strokeDasharray="5 5"
                            dot={false}
                          />
                        </>
                      )}
                    </LineChart>
                  </ResponsiveContainer>
                </Col>
                <Col span={6}>
                  {renderModelMetrics()}
                  {renderFeatureImportance()}
                </Col>
              </Row>
            )}
          </TabPane>
          <TabPane tab="Scenarios" key="2">
            {renderScenarios()}
          </TabPane>
          <TabPane tab="Balance Sheet" key="3">
            <Card title="Balance Sheet Predictions">
              <p>Balance sheet prediction functionality will be implemented here.</p>
              <p>This will include predictions for assets, liabilities, and equity based on historical trends and business drivers.</p>
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default PredictionModule;