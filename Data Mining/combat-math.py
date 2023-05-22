import math
import matplotlib
from matplotlib.axes import Axes
from matplotlib import pyplot
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline

class Global:
    WoundedDamageMultiplier = 33.0
    MaxHitPoints = 100.0
    AttackSameStrengthMinDamage = 2400.0
    AttackSameStrengthPossibleExtraDamage = 1200.0
    CityAttackingDamageMod = 100.0
    AttackingCityMeleeDamageMod = 100.0

class Unit:
    @staticmethod
    def GetProjectedDamage(
        strength: float,
        opponentStrength: float,
        currentDamage: float
    ):
        if strength == 0:
            return 0

        damageRatio = Global.MaxHitPoints \
            - currentDamage * Global.WoundedDamageMultiplier / 100.0
        damage = Global.AttackSameStrengthMinDamage \
            * damageRatio / Global.MaxHitPoints

        roll = (Global.AttackSameStrengthPossibleExtraDamage - 1.0) \
            * damageRatio / Global.MaxHitPoints / 2.0

        damage += roll

        strengthRatio = strength / opponentStrength
        if opponentStrength > strength:
            strengthRatio = opponentStrength / strength

        strengthRatio = ((((strengthRatio + 3.0) / 4.0)**4.0 + 1.0) / 2.0)
        if opponentStrength > strength:
            strengthRatio = 1.0 / strengthRatio

        damage *= strengthRatio
        damage = float(int(damage)) # Truncate

        damage /= 100.0
        if damage <= 1.0:
            damage = 1.0
        elif damage > 100.0:
            damage = 100.0

        return int(damage) # Truncate again

class Chart:
    @staticmethod
    def ColorChart():
        resolution = 2

        xValues = list(range(resolution, 101, resolution))
        yValues = list(range(resolution, 101, resolution))

        grid = np.array([[Unit.GetProjectedDamage(x, y, 0.0) for x in xValues] for y in yValues])

        fig, ax = pyplot.subplots()
        im = ax.imshow(grid, cmap="inferno", vmin=0.0, vmax = 100.0, origin="lower")

        ticks =\
        [
            str(t) if i % 2 == 0 else ""
            for (i, t) in zip(range(1, 51), range(resolution, 101, resolution))
        ]

        ax.set_xlabel("Unit Strength", fontsize=13)
        ax.set_xticks(range(len(ticks)), labels=ticks)
        ax.set_ylabel("Enemy Strength", fontsize=13)
        ax.set_yticks(range(len(ticks)), labels=ticks)

        ax.tick_params(axis='both', labelsize=12)

        fig.tight_layout()
        pyplot.colorbar(im)
        pyplot.show()

    @staticmethod
    def RatioChart():
        #xValues = np.linspace(start=0.0, stop=5.0, num=100, endpoint=False)
        xValuesLow = np.linspace(start=0.0, stop=1.0, num=50, endpoint=True)
        xValuesHigh = np.linspace(start=1.0, stop=4.0, num=50, endpoint=True)
        xLabelsLow = np.linspace(start=0.0, stop=0.75, num=4, endpoint=True)
        xLabelsHigh = np.linspace(start=1.0, stop=4.0, num=4, endpoint=True)
        yValuesLow = [Unit.GetProjectedDamage(20 * x, 20, 0) for x in xValuesLow]
        yValuesHigh = [Unit.GetProjectedDamage(20 * x, 20, 0) for x in xValuesHigh]

        #spline = make_interp_spline(xValues, yValues, k=7)
        #powerSmooth = spline(xValues)

        ax1: Axes
        ax2: Axes
        fig, (ax1, ax2) = pyplot.subplots(
            1, 2, sharey=True,
            gridspec_kw = { "wspace": 0 }
        )
        #ax1.plot(xValuesLow, yValuesLow, linewidth=5)
        #ax2.plot(xValuesHigh, yValuesHigh, linewidth=5)
        pyplot.setp(ax2.get_yticklabels(), visible=False)
        pyplot.setp(ax2.get_yticklines(), visible=False)
        ax2.spines['left'].set_visible(False)

        for ax, data, spine, ticks, labels in zip(
            (ax1, ax2),
            (yValuesLow, yValuesHigh),
            ('right', 'left'),
            (xValuesLow, xValuesHigh),
            (xLabelsLow, xLabelsHigh)
        ):
            ax.plot(ticks, data, linewidth=3)
            #ax.spines[spine].set_visible(False)
            ax.set_xticks(labels)

        ax1.set_xlim(right=1.0)
        ax2.set_xlim(left=1.0)

        ax1.set_ylim(bottom=0)
        ax2.set_ylim(bottom=0)

        for tick in xLabelsLow:
            ax1.axvline(tick, linestyle='--', linewidth=1, alpha=0.2)
        for tick in xLabelsHigh:
            ax2.axvline(tick, linestyle='--', linewidth=1, alpha=0.2)

        #ax.tick_params(axis='both', labelsize=15, )

        ax1.set_xlabel("Unit Strength ÷ Enemy Strength", fontsize=16, x=1, labelpad=10)
        ax1.tick_params(axis='both', labelsize=12)
        ax2.tick_params(axis='both', labelsize=12)
        ax1.set_ylabel("Mean Damage", fontsize=16)

        pyplot.show()

    @staticmethod
    def RatioLogChart():
        xValues = np.geomspace(start=0.01, stop=4.0, num=100, endpoint=True)
        #xValues = np.linspace(start=0.0, stop=4.0, num=100, endpoint=True)
        yValues = [Unit.GetProjectedDamage(20 * x, 20, 0) for x in xValues]

        fig, ax = pyplot.subplots()

        #ax.set_xscale('log', base=2)
        ax.set_yscale('log', base=2)

        ax.plot(xValues, yValues, linewidth=3)

        ax.axvline(1.0, linestyle='--', linewidth=1, alpha=0.5)

        #ax.set_xlim(left=0.125, right=4.0)
        #ax.set_xticks([0.01, 0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0])
        #ax.set_xticklabels([0.01, 0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0])
        #xticks = [0.125, 0.25, 0.5, 1.0, 2.0, 4.0]
        #ax.set_xticks(xticks)
        #ax.set_xticklabels(xticks)
        #for tick in xticks:
        #    ax.axvline(tick, linestyle='--', linewidth=1, alpha=0.2)

        ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        ax.set_xlabel("Unit Strength ÷ Enemy Strength", fontsize=16, labelpad=10)
        ax.tick_params(axis='both', labelsize=12)
        ax.set_ylabel("Mean Damage", fontsize=16)

        pyplot.show()

pyplot.style.use('dark_background')
Chart.ColorChart()
Chart.RatioChart()
Chart.RatioLogChart()
