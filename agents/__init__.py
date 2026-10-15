"""Farm AI - 9 Agent System"""
from agents.soil_agent import SoilAgent
from agents.irrigation_agent import IrrigationAgent
from agents.pest_agent import PestAgent
from agents.yield_agent import YieldAgent
from agents.fertilizer_agent import FertilizerAgent
from agents.harvest_agent import HarvestAgent
from agents.market_agent import MarketAgent
from agents.leaf_scan_agent import LeafScanAgent
from agents.digital_twin_agent import DigitalTwinAgent

ALL_AGENTS = [
    SoilAgent, IrrigationAgent, PestAgent, YieldAgent,
    FertilizerAgent, HarvestAgent, MarketAgent,
    LeafScanAgent, DigitalTwinAgent
]
