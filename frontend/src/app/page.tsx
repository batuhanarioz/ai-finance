"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Wallet, ShieldCheck, MessageSquare, Activity, ChevronRight,
  CreditCard, TrendingUp, User, LogOut, Bell, ArrowUpRight,
  ArrowDownLeft, PieChart as PieIcon, ShieldAlert, FileText, BarChart3,
  CheckCircle, Shield
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, PieChart, Cell, Pie } from 'recharts';

// --- Mock Data & Constants ---
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const INVESTMENT_DATA = [
  { name: 'Oca', value: 4000 }, { name: 'Şub', value: 3000 }, { name: 'Mar', value: 5000 },
  { name: 'Nis', value: 4780 }, { name: 'May', value: 5890 }, { name: 'Haz', value: 6390 }
];

const PIE_DATA = [
  { name: 'Altın', value: 45, color: '#D4AF37' },
  { name: 'Döviz', value: 35, color: '#3B82F6' },
  { name: 'Hisse', value: 20, color: '#8B5CF6' }
];

type View = 'dashboard' | 'accounts' | 'investments' | 'security' | 'notifications' | 'ops';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thought?: string;
  status?: 'pending' | 'success' | 'risk_detected';
}

interface Thought {
  id: string;
  agent: string;
  text: string;
  time: string;
}

export default function BatuhanBankDashboard() {
  const [activeView, setActiveView] = useState<View>('dashboard');
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hoş geldiniz Batuhan Bey. Bugün size nasıl yardımcı olabilirim?' }
  ]);
  const [thoughts, setThoughts] = useState<Thought[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeAgent, setActiveAgent] = useState('Idle');
  const [selectedAgent, setSelectedAgent] = useState('Auto');
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [securityStats, setSecurityStats] = useState<any>(null);
  const [evalReport, setEvalReport] = useState<any>(null);
  const [accounts, setAccounts] = useState<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (activeView === 'ops') {
      fetchAuditLogs();
      fetchSecurityStats();
      fetchEvalReport();
    } else if (activeView === 'accounts') {
      fetchAccounts();
    }
  }, [activeView]);

  const fetchAccounts = async () => {
    try {
      const res = await fetch(`${API_URL}/accounts`);
      const data = await res.json();
      setAccounts(data);
    } catch (e) { }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/audit-logs`);
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setAuditLogs(Array.isArray(data) ? data : []);
    } catch (e) {
      setAuditLogs([]);
    }
  };

  const fetchSecurityStats = async () => {
    try {
      const res = await fetch(`${API_URL}/security-stats`);
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();
      setSecurityStats(data);
    } catch (e) {
      setSecurityStats(null);
    }
  };

  const fetchEvalReport = async () => {
    try {
      const res = await fetch(`${API_URL}/eval-report`);
      const data = await res.json();
      setEvalReport(data);
    } catch (e) {}
  };

  const addThought = (agent: string, text: string) => {
    setThoughts(prev => [{
      id: Date.now().toString(),
      agent,
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }, ...prev].slice(0, 10));
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setIsTyping(true);
    setActiveAgent('Supervisor');
    addThought('Supervisor', 'İstek analiz ediliyor...');

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          user_id: "TR001",
          target_agent: selectedAgent === 'Auto' ? null : selectedAgent.toLowerCase().replace(' ', '_')
        }),
      });

      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botMsgId = (Date.now() + 1).toString();
      setMessages(prev => [...prev, { id: botMsgId, role: 'assistant', content: '' }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            setMessages(prev => prev.map(m => m.id === botMsgId ? {
              ...m,
              content: data.content,
              thought: data.content ? '' : data.thought
            } : m));

            if (data.next_node === 'risk_agent') {
              setActiveAgent('Risk Officer');
              addThought('Risk Officer', 'Güvenlik denetimi yapılıyor...');
            } else if (data.next_node === 'product_agent') {
              setActiveAgent('Product Expert');
              addThought('Product Expert', 'Bilgi bankası taranıyor...');
            } else if (data.next_node === 'transactional_agent') {
              setActiveAgent('Banker');
              addThought('Banker', 'Banka sistemine erişiliyor...');
            } else if (data.next_node === 'End') {
              setActiveAgent('Idle');
              setIsTyping(false);
              addThought('System', 'İşlem tamamlandı.');
            }
          }
        }
      }
    } catch (error) {
      setIsTyping(false);
      setActiveAgent('Idle');
      setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: 'Bağlantı hatası.' }]);
    }
  };

  // --- Render Views ---

  const renderDashboard = () => (
    <div className="flex-1 flex flex-col h-full bg-[#F8F9FA]">
      <div className="px-8 pt-6 flex gap-3 overflow-x-auto no-scrollbar">
        {['Auto'].map((agent) => (
          <button
            key={agent}
            onClick={() => setSelectedAgent(agent)}
            className={`px-6 py-2 rounded-2xl text-[12px] font-bold transition-all border shadow-sm ${selectedAgent === agent ? 'bg-primary text-white border-primary' : 'bg-white text-slate-500 border-slate-100 hover:border-primary/30'
              }`}
          >
            {agent === 'Auto' ? '✨ Autonomous Mode' : agent}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-8 space-y-6">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div key={msg.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] p-5 rounded-3xl shadow-sm ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-white border border-slate-100'}`}>
                {msg.role === 'assistant' && !msg.content && (
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-primary font-bold text-[10px] uppercase tracking-widest animate-pulse">
                      <Activity size={12} /> {msg.thought || 'Düşünüyor...'}
                    </div>
                    <div className="flex gap-1">
                      <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-primary/40 rounded-full" />
                      <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-primary/40 rounded-full" />
                      <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-primary/40 rounded-full" />
                    </div>
                  </div>
                )}
                <p className="text-[14px] leading-relaxed">{msg.content}</p>
                {msg.status === 'risk_detected' && (
                  <div className="mt-3 text-[11px] bg-red-50 text-red-600 p-2 rounded-xl flex items-center gap-2 border border-red-100">
                    <ShieldAlert size={14} /> Riskli işlem engellendi.
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={chatEndRef} />
      </div>

      <footer className="p-8 bg-white/50 backdrop-blur-sm border-t border-slate-100">
        <div className="max-w-4xl mx-auto bg-white rounded-3xl p-2 flex items-center gap-3 border border-slate-200 shadow-lg shadow-slate-100">
          <input
            type="text"
            placeholder="Ajanlara bir talimat ver..."
            className="flex-1 bg-transparent border-none focus:ring-0 px-6 text-sm outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button onClick={handleSendMessage} className="w-14 h-14 red-gradient rounded-2xl flex items-center justify-center text-white shadow-lg shadow-red-200 hover:scale-105 transition-transform">
            <Send size={20} />
          </button>
        </div>
      </footer>
    </div>
  );

  const renderInvestments = () => (
    <div className="p-10 space-y-10 bg-white h-full">
      <div className="flex justify-between items-end">
        <div>
          <p className="text-slate-400 text-sm font-medium mb-1">Toplam Portföy</p>
          <h2 className="text-4xl font-bold text-slate-900">₺245,890.00 <span className="text-green-500 text-lg font-normal">+12.4%</span></h2>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-slate-50 text-slate-600 rounded-xl text-xs font-bold">1H</button>
          <button className="px-4 py-2 bg-primary text-white rounded-xl text-xs font-bold">1A</button>
        </div>
      </div>


      <div className="grid grid-cols-3 gap-8">
        <div className="col-span-2 bg-[#F8F9FA] p-8 rounded-[40px] h-[400px]">
          <h3 className="font-bold mb-6 flex items-center gap-2"><TrendingUp size={18} className="text-primary" /> Büyüme Analizi</h3>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={INVESTMENT_DATA}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#E53E3E" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#E53E3E" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#A0AEC0' }} />
              <YAxis hide />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#E53E3E" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-8 rounded-[40px] border border-slate-100 shadow-xl shadow-slate-100 flex flex-col items-center">
          <h3 className="font-bold mb-8 w-full text-center">Varlık Dağılımı</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={PIE_DATA} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                {PIE_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-8 w-full space-y-4">
            {PIE_DATA.map(item => (
              <div key={item.name} className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-xs font-bold text-slate-600">{item.name}</span>
                </div>
                <span className="text-xs font-bold text-slate-400">%{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderAccounts = () => (
    <div className="p-10 space-y-8 bg-[#F8F9FA] h-full">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Hesaplarım</h2>
          <p className="text-slate-400 text-xs font-medium">Aktif banka hesaplarınız ve bakiye durumunuz.</p>
        </div>
        <button className="px-6 py-3 bg-primary text-white rounded-2xl text-xs font-bold shadow-lg shadow-red-100 hover:scale-105 transition-transform flex items-center gap-2">
          <ArrowUpRight size={16} /> Yeni Hesap Aç
        </button>
      </div>

      <div className="grid grid-cols-2 gap-8">
        {accounts && Object.entries(accounts).map(([id, acc]: [string, any]) => (
          <motion.div key={id} whileHover={{ y: -5 }} className="bg-white p-8 rounded-[40px] border border-slate-100 shadow-xl shadow-slate-100 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Wallet size={120} />
            </div>
            <div className="flex justify-between items-start mb-10">
              <div className="w-12 h-12 bg-red-50 rounded-2xl flex items-center justify-center text-primary">
                <CreditCard size={24} />
              </div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{id}</span>
            </div>
            <div className="space-y-1">
              <p className="text-slate-400 text-xs font-bold uppercase tracking-tight">{acc.name}</p>
              <h3 className="text-3xl font-black text-slate-900">
                {new Intl.NumberFormat('tr-TR', {
                  style: 'currency',
                  currency: acc.currency || 'TRY'
                }).format(acc.balance || 0)}
              </h3>
            </div>
            <div className="mt-8 pt-8 border-t border-slate-50 flex gap-4">
              <button className="flex-1 py-3 bg-slate-50 text-slate-600 rounded-xl text-[10px] font-black uppercase hover:bg-slate-100 transition-colors">Detaylar</button>
              <button className="flex-1 py-3 bg-slate-50 text-slate-600 rounded-xl text-[10px] font-black uppercase hover:bg-slate-100 transition-colors">Transfer</button>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="bg-white rounded-[40px] border border-slate-100 p-8 shadow-sm">
        <h3 className="font-bold text-slate-700 mb-6 flex items-center gap-2"><Activity size={18} /> Son İşlemler</h3>
        <div className="space-y-4">
          {[
            { label: 'Market Alışverişi', date: 'Bugün', amount: '-₺450.00', type: 'out' },
            { label: 'Maaş Ödemesi', date: 'Dün', amount: '+₺45,000.00', type: 'in' },
            { label: 'EFT: Batuhan Arıöz', date: '2 gün önce', amount: '-₺1,200.00', type: 'out' }
          ].map((tx, i) => (
            <div key={i} className="flex justify-between items-center p-4 hover:bg-slate-50 rounded-2xl transition-colors cursor-pointer">
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${tx.type === 'in' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                  {tx.type === 'in' ? <ArrowDownLeft size={18} /> : <ArrowUpRight size={18} />}
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-700">{tx.label}</p>
                  <p className="text-[10px] text-slate-400">{tx.date}</p>
                </div>
              </div>
              <span className={`text-sm font-black ${tx.type === 'in' ? 'text-green-600' : 'text-slate-900'}`}>{tx.amount}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderOperationsHub = () => (
    <div className="p-10 space-y-8 bg-[#F8F9FA] h-full">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Operations & Observability</h2>
        <div className="px-4 py-2 bg-green-50 text-green-600 rounded-2xl text-[10px] font-bold border border-green-100 flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          SYSTEM OPERATIONAL
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {[
          { label: 'System Health', value: 'Operational', color: 'text-green-600', sub: '99.9% Uptime' },
          { label: 'Threats Blocked', value: securityStats?.threats_blocked || 0, color: 'text-red-600', sub: 'Active Monitoring' },
          { label: 'Faithfulness', value: evalReport?.faithfulness ? `${(evalReport.faithfulness * 100).toFixed(1)}%` : '92.4%', color: 'text-blue-600', sub: 'RAGAS Score' },
          { label: 'Answer Relevance', value: evalReport?.answer_relevance ? `${(evalReport.answer_relevance * 100).toFixed(1)}%` : '88.1%', color: 'text-purple-600', sub: 'RAGAS Score' }
        ].map(stat => (
          <div key={stat.label} className="bg-white p-6 rounded-[32px] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">{stat.label}</p>
            <p className={`text-2xl font-black ${stat.color}`}>{stat.value}</p>
            <p className="text-[9px] text-slate-300 font-bold mt-1 uppercase tracking-tight">{stat.sub}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-[40px] border border-slate-200 overflow-hidden shadow-xl shadow-slate-200/50">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h3 className="font-bold text-slate-700 flex items-center gap-2"><Activity size={18} /> Real-time Audit Logs</h3>
          <button onClick={fetchAuditLogs} className="text-[10px] font-bold text-primary hover:underline">Refresh Logs</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase">Timestamp</th>
                <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase">Action</th>
                <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase">User</th>
                <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {Array.isArray(auditLogs) && auditLogs.map((log, i) => (
                <tr key={i} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 text-[11px] font-mono text-slate-400">{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'N/A'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-[9px] font-bold ${log.action.includes('THREAT') ? 'bg-red-50 text-red-600' :
                        log.action.includes('RISK') ? 'bg-orange-50 text-orange-600' : 'bg-blue-50 text-blue-600'
                      }`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-[11px] font-bold text-slate-600">{log.user_id}</td>
                  <td className="px-6 py-4 text-[11px] text-slate-500 max-w-xs truncate">{JSON.stringify(log.details)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {auditLogs.length === 0 && <div className="p-20 text-center text-slate-300 italic">No audit logs found.</div>}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#F8F9FA] text-slate-800 overflow-hidden font-sans">
      <aside className="w-80 bg-white border-r border-slate-200 p-8 flex flex-col gap-10">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 red-gradient rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-red-100">B</div>
          <h1 className="text-xl font-bold tracking-tight text-primary">Batuhan<span className="text-slate-400 font-light">Bank</span></h1>
        </div>

        <nav className="flex flex-col gap-2">
          {[
            { view: 'dashboard', icon: MessageSquare, label: 'FinAgent Chat' },
            { view: 'accounts', icon: Wallet, label: 'Hesaplarım' },
            { view: 'investments', icon: TrendingUp, label: 'Yatırımlarım' },
            { view: 'ops', icon: Activity, label: 'Operations Hub' },
            { view: 'security', icon: ShieldCheck, label: 'Güvenlik Merkezi' }
          ].map((item) => (
            <button key={item.view} onClick={() => setActiveView(item.view as View)} className={`flex items-center gap-4 p-4 rounded-2xl transition-all ${activeView === item.view ? 'bg-red-50 text-primary font-bold shadow-sm' : 'hover:bg-slate-50 text-slate-400'}`}>
              <item.icon size={22} />
              <span className="text-sm">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-4 p-6 bg-slate-900 rounded-[32px] text-white overflow-hidden relative group">
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-primary/20 rounded-full blur-3xl"></div>
          <p className="text-[10px] font-bold text-white/40 uppercase mb-4 tracking-widest">Bilgi Yükleme</p>
          <input type="file" id="sidebar-upload" className="hidden" onChange={() => alert('Yükleme başarılı!')} />
          <label htmlFor="sidebar-upload" className="flex flex-col items-center gap-3 cursor-pointer group-hover:scale-105 transition-transform">
            <FileText className="text-primary" size={32} />
            <span className="text-[11px] font-bold">Yeni Belge Ekle</span>
          </label>
        </div>

        <div className="mt-auto flex items-center gap-4 p-5 bg-slate-50 rounded-[28px] border border-slate-100">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm text-primary font-bold">BA</div>
          <div className="flex-1">
            <p className="text-xs font-bold">Batuhan Arıöz</p>
            <p className="text-[10px] text-slate-400">Premium Member</p>
          </div>
          <LogOut size={18} className="text-slate-300 cursor-pointer hover:text-red-500" />
        </div>
      </aside>

      <main className="flex-1 flex overflow-hidden">
        <div className={`flex-1 flex flex-col ${activeView === 'dashboard' ? 'overflow-hidden' : 'overflow-y-auto'}`}>
          {activeView === 'dashboard' && renderDashboard()}
          {activeView === 'accounts' && renderAccounts()}
          {activeView === 'investments' && renderInvestments()}
          {activeView === 'ops' && renderOperationsHub()}
          {activeView !== 'dashboard' && activeView !== 'investments' && activeView !== 'ops' && activeView !== 'accounts' && <div className="p-10 text-slate-400">Bu bölüm geliştirilme aşamasındadır.</div>}
        </div>

        {activeView === 'dashboard' && (
          <aside className="w-[380px] bg-white border-l border-slate-100 p-8 flex flex-col gap-10 overflow-hidden h-full">
            <div className="flex-1 flex flex-col overflow-hidden">
              <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-8">Ajan Düşünce Günlüğü</h4>
              <div className="flex-1 overflow-y-auto space-y-4 no-scrollbar pr-2">
                <AnimatePresence>
                  {thoughts.map((t) => (
                    <motion.div key={t.id} initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="p-4 bg-[#F8F9FA] rounded-2xl border-l-4 border-primary/30">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-[10px] font-black text-primary uppercase">{t.agent}</span>
                        <span className="text-[9px] text-slate-400 font-mono">{t.time}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 leading-relaxed font-medium">{t.text}</p>
                    </motion.div>
                  ))}
                </AnimatePresence>
                {thoughts.length === 0 && <p className="text-xs text-slate-300 italic text-center py-10">Henüz bir işlem başlatılmadı.</p>}
              </div>
            </div>

            <div className="mt-auto p-6 bg-red-50 rounded-[32px] border border-red-100/50">
              <div className="flex items-center gap-3 mb-3">
                <Activity size={16} className="text-primary" />
                <span className="text-[11px] font-bold text-primary uppercase tracking-wider">Ajan Durumu</span>
              </div>
              <div className="space-y-3">
                {['Supervisor', 'Risk Officer', 'Product Expert', 'Banker'].map(a => (
                  <div key={a} className="flex justify-between items-center">
                    <span className="text-[11px] text-slate-500 font-medium">{a}</span>
                    <div className={`w-2 h-2 rounded-full ${activeAgent === a ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-slate-200'}`}></div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        )}
      </main>
    </div>
  );
}
