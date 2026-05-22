import { X, Cpu } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  selectedModel: string;
  onModelChange: (model: string) => void;
}

const MODELS = [
  { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', desc: 'Best reasoning quality, slower' },
  { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', desc: 'Good balance of speed and quality' },
  { id: 'mistral-large2', name: 'Mistral Large 2', desc: 'Fast, good for general questions' },
  { id: 'llama3.1-70b', name: 'Llama 3.1 70B', desc: 'Open-source, fast responses' },
];

export default function SettingsPanel({ isOpen, onClose, selectedModel, onModelChange }: Props) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-semibold text-lg flex items-center gap-2">
            <Cpu className="w-5 h-5 text-comcast-blue" /> Settings
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">LLM Model</h3>
          <div className="space-y-2">
            {MODELS.map(model => (
              <label key={model.id} className={`flex items-center p-3 rounded-lg border cursor-pointer transition ${selectedModel === model.id ? 'border-comcast-blue bg-comcast-lightblue' : 'border-gray-200 hover:border-gray-300'}`}>
                <input type="radio" name="model" value={model.id} checked={selectedModel === model.id} onChange={() => onModelChange(model.id)} className="mr-3" />
                <div>
                  <div className="font-medium text-sm">{model.name}</div>
                  <div className="text-xs text-gray-500">{model.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>
        <div className="p-4 border-t bg-gray-50 rounded-b-xl">
          <button onClick={onClose} className="w-full py-2 bg-comcast-blue text-white rounded-lg font-medium hover:bg-comcast-darkblue transition">
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
