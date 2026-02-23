import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface TurnTimerProps {
  timeRemaining: number;
  isMyTurn: boolean;
}

export default function TurnTimer({ timeRemaining, isMyTurn }: TurnTimerProps) {
  const [seconds, setSeconds] = useState(timeRemaining);

  useEffect(() => {
    setSeconds(timeRemaining);
  }, [timeRemaining]);

  useEffect(() => {
    if (seconds <= 0) return;
    const timer = setInterval(() => {
      setSeconds(prev => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [seconds]);

  if (!isMyTurn || seconds <= 0) return null;

  const urgent = seconds <= 10;

  return (
    <div className={cn(
      'fixed top-1/2 right-4 -translate-y-1/2 rounded-xl px-4 py-3 text-center shadow-lg z-40 transition-colors',
      urgent ? 'bg-destructive text-white animate-pulse' : 'bg-card border border-border',
    )}>
      <div className="text-xs text-muted-foreground mb-1">{isMyTurn ? 'Your turn!' : ''}</div>
      <div className={cn('text-2xl font-bold font-mono', urgent && 'text-white')}>
        {seconds}s
      </div>
    </div>
  );
}
