# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jul 30 2019)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.adv

wx.ID_ADDFILE = 1000
wx.ID_REMOVEFILE = 1001
wx.ID_VIEWFILE = 1002
wx.ID_MONTECARLOCHECKBOX = 1003
wx.ID_CLUSTERCHECKBOX = 1004
wx.ID_OTHERSUFFIXCHECKBOX = 1005
wx.ID_SAVELOGCHECKBOX = 1006
wx.ID_START = 1007

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.CLOSE_BOX|wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )

		MainSizer = wx.FlexGridSizer( 2, 1, 0, 0 )
		MainSizer.SetFlexibleDirection( wx.BOTH )
		MainSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		TopSizer = wx.GridBagSizer( 0, 0 )
		TopSizer.SetFlexibleDirection( wx.BOTH )
		TopSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.InputPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.InputPanel.SetMinSize( wx.Size( 400,200 ) )

		InputPanelSizer = wx.StaticBoxSizer( wx.StaticBox( self.InputPanel, wx.ID_ANY, u"Input files" ), wx.VERTICAL )

		InputButtonSizer = wx.GridSizer( 1, 3, 0, 0 )

		self.AddButton = wx.Button( InputPanelSizer.GetStaticBox(), wx.ID_ADDFILE, u"&Add...", wx.Point( -1,-1 ), wx.DefaultSize, 0 )

		self.AddButton.SetDefault()
		InputButtonSizer.Add( self.AddButton, 1, wx.ALL, 5 )

		self.RemoveButton = wx.Button( InputPanelSizer.GetStaticBox(), wx.ID_REMOVEFILE, u"&Remove", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		InputButtonSizer.Add( self.RemoveButton, 0, wx.ALL, 5 )

		self.ViewButton = wx.Button( InputPanelSizer.GetStaticBox(), wx.ID_VIEWFILE, u"&View", wx.DefaultPosition, wx.DefaultSize, 0 )
		InputButtonSizer.Add( self.ViewButton, 0, wx.ALL, 5 )


		InputPanelSizer.Add( InputButtonSizer, 0, 0, 5 )

		self.InputFileListCtrl = wx.ListCtrl( InputPanelSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.InputFileListCtrl.SetMinSize( wx.Size( 400,-1 ) )

		InputPanelSizer.Add( self.InputFileListCtrl, 1, wx.ALL|wx.EXPAND, 5 )


		self.InputPanel.SetSizer( InputPanelSizer )
		self.InputPanel.Layout()
		InputPanelSizer.Fit( self.InputPanel )
		TopSizer.Add( self.InputPanel, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.OptionsPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		OptionsPanelSizer = wx.StaticBoxSizer( wx.StaticBox( self.OptionsPanel, wx.ID_ANY, u"Options" ), wx.VERTICAL )

		self.OptionsNotebook = wx.Notebook( OptionsPanelSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.AnalysisOptionsTab = wx.Panel( self.OptionsNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		AnalysisOptionsSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
		AnalysisOptionsSizer.SetFlexibleDirection( wx.BOTH )
		AnalysisOptionsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		GenAnalysisOptionsSizer = wx.FlexGridSizer( 2, 3, 0, 0 )
		GenAnalysisOptionsSizer.SetFlexibleDirection( wx.BOTH )
		GenAnalysisOptionsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.SpatResLabel = wx.StaticText( self.AnalysisOptionsTab, wx.ID_ANY, u"Spatial resolution:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SpatResLabel.Wrap( -1 )

		self.SpatResLabel.SetToolTip( u"Spatial resolution of the point pattern" )

		GenAnalysisOptionsSizer.Add( self.SpatResLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.SpatResSpinCtrl = wx.SpinCtrl( self.AnalysisOptionsTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 75,-1 ), wx.SP_ARROW_KEYS, 0, 1000, 25 )
		self.SpatResSpinCtrl.SetToolTip( u"Spatial resolution of the point pattern" )

		GenAnalysisOptionsSizer.Add( self.SpatResSpinCtrl, 0, wx.ALL, 5 )

		self.SpatResUnitLabel = wx.StaticText( self.AnalysisOptionsTab, wx.ID_ANY, u"metric units", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.SpatResUnitLabel.Wrap( -1 )

		self.SpatResUnitLabel.SetToolTip( u"Spatial resolution of the point pattern" )

		GenAnalysisOptionsSizer.Add( self.SpatResUnitLabel, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.ShellWidthLabel = wx.StaticText( self.AnalysisOptionsTab, wx.ID_ANY, u"Shell width:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.ShellWidthLabel.Wrap( -1 )

		self.ShellWidthLabel.SetToolTip( u"Points farther than this from the postsynaptic element are discarded" )

		GenAnalysisOptionsSizer.Add( self.ShellWidthLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.ShellWidthSpinCtrl = wx.SpinCtrl( self.AnalysisOptionsTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 75,-1 ), wx.SP_ARROW_KEYS, 0, 1000, 200 )
		self.ShellWidthSpinCtrl.SetToolTip( u"Points farther than this from the postsynaptic element are discarded" )

		GenAnalysisOptionsSizer.Add( self.ShellWidthSpinCtrl, 0, wx.ALL, 5 )

		self.ShellWidthUnitLabel = wx.StaticText( self.AnalysisOptionsTab, wx.ID_ANY, u"metric units", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.ShellWidthUnitLabel.Wrap( -1 )

		self.ShellWidthUnitLabel.SetToolTip( u"Points farther than this from the postsynaptic element are discarded" )

		GenAnalysisOptionsSizer.Add( self.ShellWidthUnitLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		AnalysisOptionsSizer.Add( GenAnalysisOptionsSizer, 1, wx.EXPAND|wx.TOP|wx.RIGHT, 5 )

		InterpointSizer = wx.StaticBoxSizer( wx.StaticBox( self.AnalysisOptionsTab, wx.ID_ANY, u"Interpoint distances" ), wx.VERTICAL )

		InterpointSizer2 = wx.GridBagSizer( 0, 0 )
		InterpointSizer2.SetFlexibleDirection( wx.BOTH )
		InterpointSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		InterpointModeChoiceChoices = []
		self.InterpointModeChoice = wx.Choice( InterpointSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, InterpointModeChoiceChoices, 0 )
		self.InterpointModeChoice.SetSelection( 0 )
		self.InterpointModeChoice.SetToolTip( u"Type of distance to calculate" )

		InterpointSizer2.Add( self.InterpointModeChoice, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		InterpointRelationsCheckListBoxChoices = [wx.EmptyString]
		self.InterpointRelationsCheckListBox = wx.CheckListBox( InterpointSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, InterpointRelationsCheckListBoxChoices, 0|wx.HSCROLL )
		InterpointSizer2.Add( self.InterpointRelationsCheckListBox, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.InterpointRelationsLabel = wx.StaticText( InterpointSizer.GetStaticBox(), wx.ID_ANY, u"Distances to\ndetermine:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.InterpointRelationsLabel.Wrap( -1 )

		InterpointSizer2.Add( self.InterpointRelationsLabel, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.InterpointModeLabel = wx.StaticText( InterpointSizer.GetStaticBox(), wx.ID_ANY, u"Distance mode:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.InterpointModeLabel.Wrap( -1 )

		self.InterpointModeLabel.SetToolTip( u"Type of distance to calculate" )

		InterpointSizer2.Add( self.InterpointModeLabel, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.InterpointCheckBox = wx.CheckBox( InterpointSizer.GetStaticBox(), wx.ID_ANY, u"Calculate interpoint distances", wx.DefaultPosition, wx.DefaultSize, 0 )
		InterpointSizer2.Add( self.InterpointCheckBox, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )

		InterpointShortLatDistSizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		InterpointShortLatDistSizer.SetFlexibleDirection( wx.BOTH )
		InterpointShortLatDistSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.ShortestDistCheckBox = wx.CheckBox( InterpointSizer.GetStaticBox(), wx.ID_ANY, u"Shortest distance", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.ShortestDistCheckBox.SetToolTip( u"Shortest distance between the points" )

		InterpointShortLatDistSizer.Add( self.ShortestDistCheckBox, 0, wx.ALL, 5 )

		self.LateralDistCheckBox = wx.CheckBox( InterpointSizer.GetStaticBox(), wx.ID_ANY, u"Distance along profile border", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.LateralDistCheckBox.SetToolTip( u"Lateral distance along profile border between the projections of the points on the border" )

		InterpointShortLatDistSizer.Add( self.LateralDistCheckBox, 0, wx.ALL, 5 )


		InterpointSizer2.Add( InterpointShortLatDistSizer, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 3 ), wx.EXPAND, 5 )


		InterpointSizer.Add( InterpointSizer2, 1, wx.EXPAND, 5 )


		AnalysisOptionsSizer.Add( InterpointSizer, 1, wx.EXPAND|wx.ALL, 5 )

		MonteCarloSizer = wx.StaticBoxSizer( wx.StaticBox( self.AnalysisOptionsTab, wx.ID_ANY, u"Monte Carlo simulations" ), wx.VERTICAL )

		MonteCarloSizer2 = wx.GridBagSizer( 0, 0 )
		MonteCarloSizer2.SetFlexibleDirection( wx.BOTH )
		MonteCarloSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.MonteCarloCheckBox = wx.CheckBox( MonteCarloSizer.GetStaticBox(), wx.ID_MONTECARLOCHECKBOX, u"Perform Monte Carlo simulations", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.MonteCarloCheckBox.SetToolTip( u"Generate a random point pattern evenly distributed over the profile (plus the shell defined by the skipping distance)" )

		MonteCarloSizer2.Add( self.MonteCarloCheckBox, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )

		self.MonteCarloRunsLabel = wx.StaticText( MonteCarloSizer.GetStaticBox(), wx.ID_ANY, u"Number of runs:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.MonteCarloRunsLabel.Wrap( -1 )

		self.MonteCarloRunsLabel.SetToolTip( u"Number of point patterns to generate for each profile" )

		MonteCarloSizer2.Add( self.MonteCarloRunsLabel, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.MonteCarloRunsSpinCtrl = wx.SpinCtrl( MonteCarloSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 75,-1 ), wx.SP_ARROW_KEYS, 1, 999, 99 )
		self.MonteCarloRunsSpinCtrl.SetToolTip( u"Number of point patterns to generate for each profile" )

		MonteCarloSizer2.Add( self.MonteCarloRunsSpinCtrl, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.SimulationWindowLabel = wx.StaticText( MonteCarloSizer.GetStaticBox(), wx.ID_ANY, u"Simulation window:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SimulationWindowLabel.Wrap( -1 )

		self.SimulationWindowLabel.SetToolTip( u"The region over which simulated points are generated" )

		MonteCarloSizer2.Add( self.SimulationWindowLabel, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		SimulationWindowChoiceChoices = []
		self.SimulationWindowChoice = wx.Choice( MonteCarloSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, SimulationWindowChoiceChoices, 0 )
		self.SimulationWindowChoice.SetSelection( 0 )
		self.SimulationWindowChoice.SetToolTip( u"The region over which simulated points are generated" )

		MonteCarloSizer2.Add( self.SimulationWindowChoice, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.StrictLocCheckBox = wx.CheckBox( MonteCarloSizer.GetStaticBox(), wx.ID_ANY, u"Strict localization in window", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.StrictLocCheckBox.SetToolTip( u"If checked, points located outside the window are excluded, even if they are within the spatial resolution of the border" )

		MonteCarloSizer2.Add( self.StrictLocCheckBox, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


		MonteCarloSizer.Add( MonteCarloSizer2, 1, wx.EXPAND, 5 )


		AnalysisOptionsSizer.Add( MonteCarloSizer, 1, wx.EXPAND|wx.ALL, 5 )

		ClusterSizer = wx.StaticBoxSizer( wx.StaticBox( self.AnalysisOptionsTab, wx.ID_ANY, u"Clusters" ), wx.VERTICAL )

		ClusterSizer2 = wx.GridBagSizer( 0, 0 )
		ClusterSizer2.SetFlexibleDirection( wx.BOTH )
		ClusterSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.ClusterCheckBox = wx.CheckBox( ClusterSizer.GetStaticBox(), wx.ID_CLUSTERCHECKBOX, u"Determine point clusters", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.ClusterCheckBox.SetToolTip( u"Partition points into clusters" )

		ClusterSizer2.Add( self.ClusterCheckBox, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )

		self.ClusterDistLabel = wx.StaticText( ClusterSizer.GetStaticBox(), wx.ID_ANY, u"Within-cluster distance:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.ClusterDistLabel.Wrap( -1 )

		self.ClusterDistLabel.SetToolTip( u"Two points closer than this distance from each other are assigned to the same cluster" )

		ClusterSizer2.Add( self.ClusterDistLabel, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

		self.ClusterDistSpinCtrl = wx.SpinCtrl( ClusterSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 75,-1 ), wx.SP_ARROW_KEYS, 1, 1000, 50 )
		self.ClusterDistSpinCtrl.SetToolTip( u"Two points closer than this distance from each other are assigned to the same cluster" )

		ClusterSizer2.Add( self.ClusterDistSpinCtrl, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.ClusterDistUnitLabel = wx.StaticText( ClusterSizer.GetStaticBox(), wx.ID_ANY, u"metric units", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
		self.ClusterDistUnitLabel.Wrap( -1 )

		self.ClusterDistUnitLabel.SetToolTip( u"Two points closer than this distance from each other are assigned to the same cluster" )

		ClusterSizer2.Add( self.ClusterDistUnitLabel, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		ClusterSizer.Add( ClusterSizer2, 1, wx.EXPAND, 5 )


		AnalysisOptionsSizer.Add( ClusterSizer, 1, wx.EXPAND|wx.ALL, 5 )


		self.AnalysisOptionsTab.SetSizer( AnalysisOptionsSizer )
		self.AnalysisOptionsTab.Layout()
		AnalysisOptionsSizer.Fit( self.AnalysisOptionsTab )
		self.OptionsNotebook.AddPage( self.AnalysisOptionsTab, u"Analysis", True )
		self.OutputOptionsTab = wx.Panel( self.OptionsNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.OutputOptionsTab.SetToolTip( u"Note: Excel output may not be available" )

		OutputOptionsSizer = wx.FlexGridSizer( 3, 2, 0, 0 )
		OutputOptionsSizer.SetFlexibleDirection( wx.BOTH )
		OutputOptionsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.SaveCoordsCheckBox = wx.CheckBox( self.OutputOptionsTab, wx.ID_ANY, u"Save processed coordinates", wx.DefaultPosition, wx.DefaultSize, 0 )
		OutputOptionsSizer.Add( self.SaveCoordsCheckBox, 0, wx.ALL, 5 )

		BlankSizer = wx.FlexGridSizer( 0, 2, 0, 0 )
		BlankSizer.SetFlexibleDirection( wx.BOTH )
		BlankSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


		OutputOptionsSizer.Add( BlankSizer, 1, wx.EXPAND, 5 )

		OutputFormatRadioBoxChoices = [ u"Excel", u"Comma-delimited text", u"Tab-delimited text" ]
		self.OutputFormatRadioBox = wx.RadioBox( self.OutputOptionsTab, wx.ID_ANY, u"Output format", wx.DefaultPosition, wx.DefaultSize, OutputFormatRadioBoxChoices, 1, wx.RA_SPECIFY_COLS )
		self.OutputFormatRadioBox.SetSelection( 0 )
		OutputOptionsSizer.Add( self.OutputFormatRadioBox, 1, wx.ALL|wx.EXPAND, 5 )

		IfOutputExistsRadioBoxChoices = [ u"Enumerate", u"Overwrite" ]
		self.IfOutputExistsRadioBox = wx.RadioBox( self.OutputOptionsTab, wx.ID_ANY, u"If output file exists", wx.DefaultPosition, wx.DefaultSize, IfOutputExistsRadioBoxChoices, 1, wx.RA_SPECIFY_COLS )
		self.IfOutputExistsRadioBox.SetSelection( 0 )
		OutputOptionsSizer.Add( self.IfOutputExistsRadioBox, 1, wx.ALL|wx.EXPAND, 5 )

		OutputFileSuffixBox = wx.StaticBoxSizer( wx.StaticBox( self.OutputOptionsTab, wx.ID_ANY, u"Output file suffix" ), wx.VERTICAL )

		self.DateSuffixCheckBox = wx.CheckBox( OutputFileSuffixBox.GetStaticBox(), wx.ID_ANY, u"Today's date", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.DateSuffixCheckBox.SetValue(True)
		OutputFileSuffixBox.Add( self.DateSuffixCheckBox, 0, wx.ALL, 5 )

		OtherSuffixSizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		OtherSuffixSizer.AddGrowableCol( 1 )
		OtherSuffixSizer.SetFlexibleDirection( wx.BOTH )
		OtherSuffixSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.OtherSuffixCheckBox = wx.CheckBox( OutputFileSuffixBox.GetStaticBox(), wx.ID_OTHERSUFFIXCHECKBOX, u"Other:", wx.DefaultPosition, wx.DefaultSize, 0 )
		OtherSuffixSizer.Add( self.OtherSuffixCheckBox, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.OtherSuffixTextCtrl = wx.TextCtrl( OutputFileSuffixBox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
		self.OtherSuffixTextCtrl.SetMaxLength( 0 )
		OtherSuffixSizer.Add( self.OtherSuffixTextCtrl, 0, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )


		OutputFileSuffixBox.Add( OtherSuffixSizer, 1, wx.EXPAND, 5 )


		OutputOptionsSizer.Add( OutputFileSuffixBox, 1, wx.EXPAND|wx.ALL, 5 )


		self.OutputOptionsTab.SetSizer( OutputOptionsSizer )
		self.OutputOptionsTab.Layout()
		OutputOptionsSizer.Fit( self.OutputOptionsTab )
		self.OptionsNotebook.AddPage( self.OutputOptionsTab, u"Output", False )
		self.LogOptionsTab = wx.Panel( self.OptionsNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		LogOptionsSizer = wx.FlexGridSizer( 2, 1, 0, 0 )
		LogOptionsSizer.SetFlexibleDirection( wx.BOTH )
		LogOptionsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		SaveLogSizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		SaveLogSizer.AddGrowableCol( 1 )
		SaveLogSizer.SetFlexibleDirection( wx.BOTH )
		SaveLogSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.SaveLogCheckBox = wx.CheckBox( self.LogOptionsTab, wx.ID_SAVELOGCHECKBOX, u"Save as:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SaveLogCheckBox.SetValue(True)
		SaveLogSizer.Add( self.SaveLogCheckBox, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.LogFilePickerCtrl = wx.FilePickerCtrl( self.LogOptionsTab, wx.ID_ANY, u"PointDensity.log", u"Select a file", u"*.log", wx.DefaultPosition, wx.DefaultSize, wx.FLP_USE_TEXTCTRL )
		SaveLogSizer.Add( self.LogFilePickerCtrl, 1, wx.ALL|wx.EXPAND, 5 )


		LogOptionsSizer.Add( SaveLogSizer, 1, wx.EXPAND, 5 )

		IfLogExistsSizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		IfLogExistsSizer.SetFlexibleDirection( wx.BOTH )
		IfLogExistsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		IfLogExistsRadioBoxChoices = [ u"Enumerate", u"Overwrite", u"Append" ]
		self.IfLogExistsRadioBox = wx.RadioBox( self.LogOptionsTab, wx.ID_ANY, u"If log file exists", wx.DefaultPosition, wx.DefaultSize, IfLogExistsRadioBoxChoices, 1, wx.RA_SPECIFY_COLS )
		self.IfLogExistsRadioBox.SetSelection( 0 )
		IfLogExistsSizer.Add( self.IfLogExistsRadioBox, 0, wx.ALL, 5 )


		LogOptionsSizer.Add( IfLogExistsSizer, 1, wx.EXPAND, 5 )


		self.LogOptionsTab.SetSizer( LogOptionsSizer )
		self.LogOptionsTab.Layout()
		LogOptionsSizer.Fit( self.LogOptionsTab )
		self.OptionsNotebook.AddPage( self.LogOptionsTab, u"Logging", False )

		OptionsPanelSizer.Add( self.OptionsNotebook, 1, wx.EXPAND |wx.ALL, 5 )

		self.SetOptionsAsDefaultButton = wx.Button( OptionsPanelSizer.GetStaticBox(), wx.ID_ANY, u"Set options as default", wx.DefaultPosition, wx.DefaultSize, 0 )
		OptionsPanelSizer.Add( self.SetOptionsAsDefaultButton, 0, wx.ALL, 5 )


		self.OptionsPanel.SetSizer( OptionsPanelSizer )
		self.OptionsPanel.Layout()
		OptionsPanelSizer.Fit( self.OptionsPanel )
		TopSizer.Add( self.OptionsPanel, wx.GBPosition( 0, 1 ), wx.GBSpan( 2, 1 ), wx.EXPAND |wx.ALL, 5 )

		self.LogPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		LogSizer = wx.StaticBoxSizer( wx.StaticBox( self.LogPanel, wx.ID_ANY, u"Log" ), wx.VERTICAL )

		self.LogTextCtrl = wx.TextCtrl( LogSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.HSCROLL|wx.TE_MULTILINE )
		self.LogTextCtrl.SetMaxLength( 0 )
		self.LogTextCtrl.SetFont( wx.Font( 8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		LogSizer.Add( self.LogTextCtrl, 1, wx.ALL|wx.EXPAND, 5 )


		self.LogPanel.SetSizer( LogSizer )
		self.LogPanel.Layout()
		LogSizer.Fit( self.LogPanel )
		TopSizer.Add( self.LogPanel, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND |wx.ALL, 5 )


		TopSizer.AddGrowableRow( 0 )

		MainSizer.Add( TopSizer, 1, wx.EXPAND, 5 )

		BottomSizer = wx.FlexGridSizer( 1, 1, 0, 0 )
		BottomSizer.AddGrowableCol( 0 )
		BottomSizer.AddGrowableRow( 0 )
		BottomSizer.SetFlexibleDirection( wx.BOTH )
		BottomSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )

		self.MainButtonPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		MainButtonSizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		MainButtonSizer.AddGrowableRow( 0 )
		MainButtonSizer.SetFlexibleDirection( wx.BOTH )
		MainButtonSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


		MainButtonSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.StartButton = wx.Button( self.MainButtonPanel, wx.ID_START, u"&Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		MainButtonSizer.Add( self.StartButton, 0, wx.ALL, 5 )

		self.AboutButton = wx.Button( self.MainButtonPanel, wx.ID_ABOUT, u"A&bout...", wx.DefaultPosition, wx.DefaultSize, 0 )
		MainButtonSizer.Add( self.AboutButton, 1, wx.ALL|wx.ALIGN_RIGHT, 5 )

		self.ExitButton = wx.Button( self.MainButtonPanel, wx.ID_EXIT, u"&Exit", wx.DefaultPosition, wx.DefaultSize, 0 )
		MainButtonSizer.Add( self.ExitButton, 1, wx.ALL|wx.ALIGN_RIGHT, 5 )


		self.MainButtonPanel.SetSizer( MainButtonSizer )
		self.MainButtonPanel.Layout()
		MainButtonSizer.Fit( self.MainButtonPanel )
		BottomSizer.Add( self.MainButtonPanel, 1, wx.ALL|wx.ALIGN_RIGHT, 5 )


		MainSizer.Add( BottomSizer, 1, wx.EXPAND|wx.ALIGN_RIGHT, 5 )


		self.SetSizer( MainSizer )
		self.Layout()
		MainSizer.Fit( self )
		self.StatusBar = self.CreateStatusBar( 1, 0, wx.ID_ANY )

		# Connect Events
		self.AddButton.Bind( wx.EVT_BUTTON, self.OnAddFile )
		self.RemoveButton.Bind( wx.EVT_BUTTON, self.OnRemoveFile )
		self.ViewButton.Bind( wx.EVT_BUTTON, self.OnViewFile )
		self.InterpointCheckBox.Bind( wx.EVT_CHECKBOX, self.OnInterpointCheckbox )
		self.MonteCarloCheckBox.Bind( wx.EVT_CHECKBOX, self.OnMonteCarloCheckBox )
		self.SimulationWindowChoice.Bind( wx.EVT_CHOICE, self.OnSimulationWindowChoice )
		self.ClusterCheckBox.Bind( wx.EVT_CHECKBOX, self.OnClusterCheckBox )
		self.OtherSuffixCheckBox.Bind( wx.EVT_CHECKBOX, self.OnOtherSuffixCheckBox )
		self.SaveLogCheckBox.Bind( wx.EVT_CHECKBOX, self.OnSaveLogCheckBox )
		self.LogFilePickerCtrl.Bind( wx.EVT_FILEPICKER_CHANGED, self.OnSaveLogCheckBox )
		self.SetOptionsAsDefaultButton.Bind( wx.EVT_BUTTON, self.OnSetOptionsAsDefault )
		self.StartButton.Bind( wx.EVT_BUTTON, self.OnStart )
		self.AboutButton.Bind( wx.EVT_BUTTON, self.OnAbout )
		self.ExitButton.Bind( wx.EVT_BUTTON, self.OnClose )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnAddFile( self, event ):
		event.Skip()

	def OnRemoveFile( self, event ):
		event.Skip()

	def OnViewFile( self, event ):
		event.Skip()

	def OnInterpointCheckbox( self, event ):
		event.Skip()

	def OnMonteCarloCheckBox( self, event ):
		event.Skip()

	def OnSimulationWindowChoice( self, event ):
		event.Skip()

	def OnClusterCheckBox( self, event ):
		event.Skip()

	def OnOtherSuffixCheckBox( self, event ):
		event.Skip()

	def OnSaveLogCheckBox( self, event ):
		event.Skip()


	def OnSetOptionsAsDefault( self, event ):
		event.Skip()

	def OnStart( self, event ):
		event.Skip()

	def OnAbout( self, event ):
		event.Skip()

	def OnClose( self, event ):
		event.Skip()


###########################################################################
## Class ViewFileDialog
###########################################################################

class ViewFileDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"View input file", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		ViewFileSizer = wx.FlexGridSizer( 2, 1, 0, 0 )
		ViewFileSizer.SetFlexibleDirection( wx.BOTH )
		ViewFileSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.ViewFileTextCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,400 ), wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY )
		self.ViewFileTextCtrl.SetMaxLength( 0 )
		ViewFileSizer.Add( self.ViewFileTextCtrl, 0, wx.ALL, 5 )

		ViewFileStdButtonSizer = wx.StdDialogButtonSizer()
		self.ViewFileStdButtonSizerOK = wx.Button( self, wx.ID_OK )
		ViewFileStdButtonSizer.AddButton( self.ViewFileStdButtonSizerOK )
		ViewFileStdButtonSizer.Realize();

		ViewFileSizer.Add( ViewFileStdButtonSizer, 1, wx.EXPAND|wx.ALL, 5 )


		self.SetSizer( ViewFileSizer )
		self.Layout()
		ViewFileSizer.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.ViewFileStdButtonSizerOK.Bind( wx.EVT_BUTTON, self.OnClose )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnClose( self, event ):
		event.Skip()


###########################################################################
## Class AboutDialog
###########################################################################

class AboutDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		AboutSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
		AboutSizer.AddGrowableRow( 2 )
		AboutSizer.SetFlexibleDirection( wx.BOTH )
		AboutSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		TopSizer = wx.FlexGridSizer( 0, 2, 10, 10 )
		TopSizer.SetFlexibleDirection( wx.BOTH )
		TopSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.InitialSpaceSizer = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.InitialSpaceSizer.Wrap( -1 )

		self.InitialSpaceSizer.SetMinSize( wx.Size( -1,5 ) )

		TopSizer.Add( self.InitialSpaceSizer, 0, wx.ALL, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		TitleSizer = wx.FlexGridSizer( 1, 3, 0, 0 )
		TitleSizer.AddGrowableCol( 2 )
		TitleSizer.SetFlexibleDirection( wx.BOTH )
		TitleSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.IconBitmap = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		TitleSizer.Add( self.IconBitmap, 0, wx.ALL, 5 )

		self.SmallSpacer = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SmallSpacer.Wrap( -1 )

		TitleSizer.Add( self.SmallSpacer, 0, wx.ALL, 5 )

		self.TitleLabel = wx.StaticText( self, wx.ID_ANY, u"TitleLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.TitleLabel.Wrap( -1 )

		self.TitleLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		TitleSizer.Add( self.TitleLabel, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		TopSizer.Add( TitleSizer, 1, wx.EXPAND|wx.RIGHT, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.VersionLabel = wx.StaticText( self, wx.ID_ANY, u"VersionLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.VersionLabel.Wrap( -1 )

		self.VersionLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		TopSizer.Add( self.VersionLabel, 0, wx.ALIGN_BOTTOM|wx.TOP|wx.RIGHT|wx.LEFT, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.LastModLabel = wx.StaticText( self, wx.ID_ANY, u"LastModLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.LastModLabel.Wrap( -1 )

		TopSizer.Add( self.LastModLabel, 0, wx.RIGHT|wx.LEFT, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.CopyrightLabel = wx.StaticText( self, wx.ID_ANY, u"CopyrightLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.CopyrightLabel.Wrap( -1 )

		TopSizer.Add( self.CopyrightLabel, 0, wx.RIGHT|wx.LEFT, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.LicenseLabel = wx.StaticText( self, wx.ID_ANY, u"LicenseLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.LicenseLabel.Wrap( -1 )

		TopSizer.Add( self.LicenseLabel, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		HyperLinksSizer = wx.FlexGridSizer( 2, 2, 0, 0 )
		HyperLinksSizer.AddGrowableCol( 1 )
		HyperLinksSizer.SetFlexibleDirection( wx.HORIZONTAL )
		HyperLinksSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.EmailLabel = wx.StaticText( self, wx.ID_ANY, u"E-mail:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.EmailLabel.Wrap( -1 )

		HyperLinksSizer.Add( self.EmailLabel, 0, wx.ALL, 5 )

		self.EmailHyperlink = wx.adv.HyperlinkCtrl( self, wx.ID_ANY, u"EmailHyperlink", wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		HyperLinksSizer.Add( self.EmailHyperlink, 0, wx.ALL, 5 )

		self.WebLabel = wx.StaticText( self, wx.ID_ANY, u"Web:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.WebLabel.Wrap( -1 )

		HyperLinksSizer.Add( self.WebLabel, 0, wx.ALL, 5 )

		self.WebHyperlink = wx.adv.HyperlinkCtrl( self, wx.ID_ANY, u"WebHyperlink", wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		HyperLinksSizer.Add( self.WebHyperlink, 0, wx.ALL, 5 )


		TopSizer.Add( HyperLinksSizer, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5 )


		TopSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		AboutSizer.Add( TopSizer, 1, wx.EXPAND, 5 )

		self.Staticline = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		AboutSizer.Add( self.Staticline, 0, wx.EXPAND |wx.ALL, 5 )

		OK_SdbSizer = wx.StdDialogButtonSizer()
		self.OK_SdbSizerOK = wx.Button( self, wx.ID_OK )
		OK_SdbSizer.AddButton( self.OK_SdbSizerOK )
		OK_SdbSizer.Realize();

		AboutSizer.Add( OK_SdbSizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.SetSizer( AboutSizer )
		self.Layout()
		AboutSizer.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.OK_SdbSizerOK.Bind( wx.EVT_BUTTON, self.OnClose )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def OnClose( self, event ):
		event.Skip()


